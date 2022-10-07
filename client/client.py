import grpc

import movie_pb2
import showtime_pb2
import booking_pb2
import movie_pb2_grpc
import showtime_pb2_grpc
import booking_pb2_grpc


def get_movie_by_id(stub, id):
    movie = stub.GetMovieByID(id)
    print(movie)

def get_list_movies(stub):
    allmovies = stub.GetListMovies(movie_pb2.Empty())
    for movie in allmovies:
        print("Movie called %s" % (movie.title))

def get_movie_by_title(stub, title):
    movie = stub.GetMovieByTitle(title)
    print(movie)

def create_movie(stub, movie):
    res = stub.CreateMovie(movie)
    print(res)

def get_movie_by_director(stub, director):
    movie = stub.GetMovieByDirector(director)
    print(movie)


def update_movie_rating(stub, movieIdRating):
    movie = stub.UpdateMovieRating(movieIdRating)
    print(movie)

def get_showtime_by_date(stub, date):
    movies = stub.GetMoviesByDate(date)
    for movie in movies:
        print(movie)

def get_list_showtimes(stub):
    allShowtimes = stub.GetAllShowtimes(showtime_pb2.EmptyShowtime())
    for show in allShowtimes:
        print('----------')
        print("Date: " + show.date)
        for movie in show.movies:
            print("  -Movie: " + movie)

def get_booking_by_userid(stub,userid):
    booking = stub.GetBookingByUserid(userid)
    print(booking)

def add_booking_by_userid(stub, booking):
    message = stub.AddBookingByUserid(booking)
    print(message)

def delete_movie_by_id(stub, id):
    message = stub.DeleteMovieById(id)
    print(message)

def run():
    # NOTE(gRPC Python Team): .close() is possible on a channel and should be
    # used in circumstances in which the with statement does not fit the needs
    # of the code.
    with grpc.insecure_channel('localhost:3001') as channel:
        stub = movie_pb2_grpc.MovieStub(channel)

        print("-------------- GetMovieByID --------------")
        movieid = movie_pb2.MovieID(id="720d006c-3a57-4b6a-b18f-9b713b073f3c")
        get_movie_by_id(stub, movieid)

        print("-------------- GetAllMovies --------------")
        get_list_movies(stub)

        print("-------------- CreateMovie --------------")
        movie = movie_pb2.MovieData(title="Ma vie", director="Ma vie", id="0", rating=100000)
        create_movie(stub, movie)

        print("-------------- GetMovieByTitle --------------")
        movieTitle = movie_pb2.MovieTitle(title="The Martian")
        get_movie_by_title(stub, movieTitle)

        print("-------------- GetMovieByDirector --------------")
        movieTitle = movie_pb2.MovieDirector(director="Jonathan Levine")
        get_movie_by_director(stub, movieTitle)

        print("-------------- UpdateMovieRating --------------")
        movieIdRating = movie_pb2.MovieIdRating(id="267eedb8-0f5d-42d5-8f43-72426b9fb3e6", rating=14.2)
        update_movie_rating(stub, movieIdRating)

        print("-------------- DeleteMovieById --------------")
        movieid = movie_pb2.MovieID(id="39ab85e5-5e8e-4dc5-afea-65dc368bd7ab")
        delete_movie_by_id(stub, movieid)

    channel.close()

    with grpc.insecure_channel('localhost:3002') as channel:
        stub = showtime_pb2_grpc.ShowtimeStub(channel)

        print("-------------- GetShowtimesByDate --------------")
        date = showtime_pb2.ShowtimeDate(date="20151130")
        get_showtime_by_date(stub, date)

        print("-------------- AllShowtimes --------------")
        get_list_showtimes(stub)

    channel.close()

    with grpc.insecure_channel('localhost:3003') as channel:
        stub = booking_pb2_grpc.BookingStub(channel)

        print("-------------- GetBookingByUserid --------------")
        userid = booking_pb2.BookingUserId(userid="dwight_schrute")
        get_booking_by_userid(stub,userid)

        print("-------------- AddBookingByUserid --------------")
        booking = booking_pb2.OneBooking(userid="dwight_schrute", date="20151201", movieid="7daf7208-be4d-4944-a3ae-c1c2f516f3e6")
        add_booking_by_userid(stub, booking)



    channel.close()

if __name__ == '__main__':
    run()
