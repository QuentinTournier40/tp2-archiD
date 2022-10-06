from flask import Flask, render_template, request, jsonify, make_response
import requests
import json
import grpc
import showtime_pb2_grpc
import showtime_pb2
import booking_pb2_grpc
import booking_pb2
from concurrent import futures
from google.protobuf.json_format import MessageToJson
from werkzeug.exceptions import NotFound

class BookingServicer(booking_pb2_grpc.BookingServicer):

    def __init__(self):
        with open('{}/data/bookings.json'.format("."), "r") as jsf:
            self.db = json.load(jsf)["bookings"]

    def GetBookingByUserid(self, request, context):
        for booking in self.db:
            if request.userid == booking["userid"]:
                allDate = []
                for dateInfos in booking["dates"]:
                    date = booking_pb2.Dates(date=dateInfos["date"], movieid=dateInfos["movies"])
                    allDate.append(date)
                return booking_pb2.BookingObject(userid=booking["userid"], dates=allDate)

    def AddBookingByUserid(self, request, context):
        scheduleExist = False

        with grpc.insecure_channel('localhost:3002') as channel:
            stub = showtime_pb2_grpc.ShowtimeStub(channel)
            schedule = stub.GetShowtimesByDate(showtime_pb2.ShowtimeDate(date=request.date))

        channel.close()

        schedule = json.loads(MessageToJson(schedule))

        for moviesShownId in schedule["movies"]:
            if request.movieid == moviesShownId:
                scheduleExist = True

        if not scheduleExist:
            return booking_pb2.NotificationMessageBooking(message="Movie not shown at this date")

        for booking in self.db:
            if str(booking["userid"]) == str(request.userid):
                bookingUser = booking
                for bookingDateInfo in booking["dates"]:
                    if bookingDateInfo["date"] == request.date:
                        for movie in bookingDateInfo["movies"]:
                            if movie == request.movieid:
                                return booking_pb2.NotificationMessageBooking(message="This booking already exists for this movie at this date")

        if 'bookingUser' in locals():
            newMovie = {
                "date": request.date,
                "movieid": request.movieid
            }
            bookingUser["dates"].append(newMovie)

            return booking_pb2.NotificationMessageBooking(message="booking added")
        else:
            return booking_pb2.NotificationMessageBooking(message="UserId not found")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    booking_pb2_grpc.add_BookingServicer_to_server(BookingServicer(), server)
    server.add_insecure_port('[::]:3003')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
