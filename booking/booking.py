import json
import grpc
import showtime_pb2_grpc
import showtime_pb2
import booking_pb2_grpc
import booking_pb2
from concurrent import futures
from google.protobuf.json_format import MessageToJson

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
        return booking_pb2.BookingObject(userid="", dates=[])

    def AddBookingByUserid(self, request, context):
        scheduleExist = False

        # Recupération des films diffusés à la date donnée
        with grpc.insecure_channel('localhost:3002') as channel:
            stub = showtime_pb2_grpc.ShowtimeStub(channel)
            schedule = stub.GetShowtimesByDate(showtime_pb2.ShowtimeDate(date=str(request.date)))

        scheduleJson = json.loads(MessageToJson(schedule))

        # Check s'il existe une programme pour cette date
        if not bool(scheduleJson):
            return booking_pb2.NotificationMessageBooking(message="0 films programed for this date")

        # Check si l'utilisateur existe
        bookingOfUser = {}
        for booking in self.db:
            if booking["userid"] == request.userid:
                bookingOfUser = booking

        if not bool(bookingOfUser):
            return booking_pb2.NotificationMessageBooking(message="Userid not found")

        # Check si le film est diffusé à la date donnée
        for moviesShownId in scheduleJson["movies"]:
            if request.movieid == moviesShownId:
                scheduleExist = True

        if not scheduleExist:
            return booking_pb2.NotificationMessageBooking(message="Movie not shown at this date")

        # Check si l'utilisateur a deja reservé un film à la date demandée
        dateInfosOfBooking = {}
        for bookingDateInfo in bookingOfUser["dates"]:
            if bookingDateInfo["date"] == str(request.date):
                dateInfosOfBooking = bookingDateInfo

        # Si il a deja un film reservé à la date demandé il faut verifier que ce n'est pas celui qu'il demande maintenant
        if bool(dateInfosOfBooking):
            for movieid in dateInfosOfBooking["movies"]:
                if movieid == request.movieid:
                    return booking_pb2.NotificationMessageBooking(message="This booking already exists for this movie at this date")

        # Mise à jour de la BDD
        indexBookingOfUser = self.db.index(bookingOfUser)
        if bool(dateInfosOfBooking):
            # Si l'user possède deja une reservation pour la date demandée
            indexDate = bookingOfUser["dates"].index(dateInfosOfBooking)
            bookingOfUser["dates"][indexDate]["movies"].append(request.movieid)
        else:
            # Si l'user ne possède pas une reservation pour la date demandée
            reqJson = json.loads(MessageToJson(request))
            bookingOfUser["dates"].append(reqJson)

        self.db[indexBookingOfUser] = bookingOfUser
        return booking_pb2.NotificationMessageBooking(message="booking added")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    booking_pb2_grpc.add_BookingServicer_to_server(BookingServicer(), server)
    server.add_insecure_port('[::]:3003')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
