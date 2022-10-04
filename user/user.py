from flask import Flask, render_template, request, jsonify, make_response
import requests
import json

import grpc
import movie_pb2_grpc
import movie_pb2

app = Flask(__name__)

PORT = 3004
HOST = '0.0.0.0'

with open('{}/data/users.json'.format("."), "r") as jsf:
   users = json.load(jsf)["users"]

def get_movie_by_id(stub, id):
   return stub.GetMovieByID(id)
@app.route("/get-movies-infos-of-selected-movies-by-userid/<userid>", methods=['GET'])
def get_movies_infos_of_selected_movies_by_userid(userid):
   moviesInfos = json.loads('{"movies": []}')
   for user in users:
      if str(user["id"]) == str(userid):
         booking = requests.get("http://172.20.190.169:3201/bookings/" + userid)

   if not 'booking' in locals():
      return make_response(jsonify({"error": "user for this userid not found"}), 400)

   if booking.status_code != 200:
      return make_response(jsonify({"error": "this userid doesn't have bookings"}), 400)

   with grpc.insecure_channel('localhost:3001') as channel:
      stub = movie_pb2_grpc.MovieStub(channel)

      for date in booking.json()["dates"]:
         for movieid in date["movies"]:
            id = movie_pb2.MovieID(id=movieid)
            movie = get_movie_by_id(stub, id)
            obj = {
               "id" : movie.id,
               "title" : movie.title,
               "rating" : movie.rating,
               "director" : movie.director
            }
            moviesInfos["movies"].append(obj)
   channel.close()

   return make_response(jsonify(moviesInfos), 200)

if __name__ == "__main__":
   print("Server running in port %s"%(PORT))
   app.run(host=HOST, port=PORT)
