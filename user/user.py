from flask import Flask, jsonify, make_response
from google.protobuf.json_format import MessageToJson
import json

import grpc
import movie_pb2_grpc
import movie_pb2
import booking_pb2
import booking_pb2_grpc

app = Flask(__name__)

PORT = 3004
HOST = 'localhost'

with open('{}/data/users.json'.format("."), "r") as jsf:
   users = json.load(jsf)["users"]

@app.route("/get-movies-infos-of-selected-movies-by-userid/<userid>", methods=['GET'])
def get_movies_infos_of_selected_movies_by_userid(userid):
   moviesInfos = {"movies": []}
   booking = ""
   userFound = False

   for user in users:
      if str(user["id"]) == str(userid):
         userFound = True
         with grpc.insecure_channel("localhost:3003") as channel:
            stub = booking_pb2_grpc.BookingStub(channel)

            userid = booking_pb2.BookingUserId(userid=user["id"])
            booking = stub.GetBookingByUserid(userid)

   if not userFound:
      return make_response(jsonify({"error": "user for this userid not found"}), 400)

   if not str(booking):
      return make_response(jsonify({"error": "this userid doesn't have bookings"}), 400)

   with grpc.insecure_channel('localhost:3001') as channel:
      stub = movie_pb2_grpc.MovieStub(channel)

      bookingJson = json.loads(MessageToJson(booking))
      for date in bookingJson["dates"]:
         for movieid in date["movieid"]:
            id = movie_pb2.MovieID(id=movieid)
            movie = stub.GetMovieByID(id)
            obj = {
               "id" : movie.id,
               "title" : movie.title,
               "rating" : movie.rating,
               "director" : movie.director
            }
            moviesInfos["movies"].append(obj)

   return make_response(jsonify(moviesInfos), 200)

if __name__ == "__main__":
   print("Server running in port %s"%(PORT))
   app.run(host=HOST, port=PORT)
