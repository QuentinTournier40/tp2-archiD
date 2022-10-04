import grpc

import movie_pb2
import movie_pb2_grpc


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


def get_movie_by_director(stub, director):
    movie = stub.GetMovieByDirector(director)
    print(movie)


def update_movie_rating(stub, movieIdRating):
    movie = stub.UpdateMovieRating(movieIdRating)
    print(movie)


def run():
    # NOTE(gRPC Python Team): .close() is possible on a channel and should be
    # used in circumstances in which the with statement does not fit the needs
    # of the code.
    with grpc.insecure_channel('localhost:3001') as channel:
        stub = movie_pb2_grpc.MovieStub(channel)

        print("-------------- GetMovieByID --------------")
        movieid = movie_pb2.MovieID(id="a8034f44-aee4-44cf-b32c-74cf452aaaae")
        get_movie_by_id(stub, movieid)

        print("-------------- GetMovieByTitle --------------")
        movieTitle = movie_pb2.MovieTitle(title="The Martian")
        get_movie_by_title(stub, movieTitle)

        print("-------------- GetMovieByDirector --------------")
        movieTitle = movie_pb2.MovieDirector(director="Jonathan Levine")
        get_movie_by_director(stub, movieTitle)

        print("-------------- UpdateMovieRating --------------")
        movieIdRating = movie_pb2.MovieIdRating(id="267eedb8-0f5d-42d5-8f43-72426b9fb3e6", rating=14.2)
        update_movie_rating(stub, movieIdRating)

    channel.close()


if __name__ == '__main__':
    run()
