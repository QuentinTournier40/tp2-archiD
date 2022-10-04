from flask import Flask, render_template, request, jsonify, make_response
import requests
import json
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



# TODO Ajouter FILM à la réservation (date/ID) + Verification de que le film ne soit pas ajouté à la même date pour cette personne
# Fonction crée par Tournier Quentin et Marche Jules
# But: Ajouter une réservation à un utilisateur
# En entrée: UserId(path)
# En sortie: Un message stipulant l'ajout de la réservation
@app.route("/bookings/<userid>", methods=['POST'])
def add_booking_byuser(userid):
   req = request.get_json()

   for booking in bookings:
      if str(booking["userid"]) == str(userid):
         return make_response(jsonify({"error": "booking ID already exists"}), 409)

   bookings.append(req)
   return make_response(jsonify({"message": "booking added"}), 200)

if __name__ == "__main__":
   print("Server running in port %s"%(PORT))
   app.run(host=HOST, port=PORT)