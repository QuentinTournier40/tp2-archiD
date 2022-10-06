from flask import Flask, render_template, request, jsonify, make_response
import requests
import json
import grpc
import showtime_pb2_grpc
import showtime_pb2
from google.protobuf.json_format import MessageToJson
from werkzeug.exceptions import NotFound

app = Flask(__name__)

PORT = 3201
HOST = '0.0.0.0'

with open('{}/data/bookings.json'.format("."), "r") as jsf:
   bookings = json.load(jsf)["bookings"]

@app.route("/", methods=['GET'])
def home():
   return "<h1 style='color:blue'>Welcome to the Booking service!</h1>"

@app.route("/bookings", methods=['GET'])
def get_json():
   return make_response(jsonify(bookings), 200)

# Fonction crée par Tournier Quentin et Marche Jules
# But: Afficher toutes les réservations d'un Utilisateur
# En entrée: UserId(path)
# En sortie: Un tableau de toutes les réservations
@app.route("/bookings/<userid>", methods=['GET'])
def get_booking_for_user(userid):
   for booking in bookings:
      if str(booking["userid"]) == str(userid):
         return make_response(jsonify(booking), 200)
   return make_response(jsonify({"error":"booking with this id not found"}),400)

def get_schedule_by_date(stub, date):
   return stub.GetMoviesByDateTmp(date)

# Fonction crée par Tournier Quentin et Marche Jules
# But: Ajouter une réservation à un utilisateur
# En entrée: UserId(path)
# En sortie: Un message stipulant l'ajout de la réservation
@app.route("/bookings/<userid>", methods=['POST'])
def add_booking_byuser(userid):
   req = request.get_json()
   scheduleExist = False

   # Récuépration des shedule et verification de la projection à la date donnée en paramètre
   with grpc.insecure_channel('localhost:3002') as channel:
      stub = showtime_pb2_grpc.ShowtimeStub(channel)

      schedule = get_schedule_by_date(stub, showtime_pb2.ShowtimeDate(date=str(req["date"])))

   channel.close()

   schedule = json.loads(MessageToJson(schedule))

   for moviesShownId in schedule["movies"]:
      if req["movieid"] == moviesShownId:
         scheduleExist = True

   if not scheduleExist:
      return make_response(jsonify({"message": "Movie not shown at this date"}), 400)

   for booking in bookings:
      if str(booking["userid"]) == str(userid):
         bookingUser = booking
         for bookingDateInfo in booking["dates"]:
            if bookingDateInfo["date"] == str(req["date"]):
               for movie in bookingDateInfo["movies"]:
                  if movie == req["movieid"] :
                     return make_response(jsonify({"error": "This booking already exists for this movie at this date"}), 409)

   if 'bookingUser' in locals():
      bookingUser["dates"].append(req)
      return make_response(jsonify({"message": "booking added"}), 200)
   else :
      return make_response(jsonify({"message": "UserId not found"}), 400)

if __name__ == "__main__":
   print("Server running in port %s"%(PORT))
   app.run(host=HOST, port=PORT)