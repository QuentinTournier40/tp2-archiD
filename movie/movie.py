import grpc
from concurrent import futures
import movie_pb2
import movie_pb2_grpc
import json

with open('{}/data/movies.json'.format("."), "r") as jsf:
   movies = json.load(jsf)["movies"]

class MovieServicer(movie_pb2_grpc.MovieServicer):

    def __init__(self):
        with open('{}/data/movies.json'.format("."), "r") as jsf:
            self.db = json.load(jsf)["movies"]

    def GetMovieByID(self, request, context):
        for movie in self.db:
            if movie['id'] == request.id:
                print("Movie found!")
                return movie_pb2.MovieData(title=movie['title'], rating=movie['rating'], director=movie['director'],
                                           id=movie['id'])
        return movie_pb2.MovieData(title="", rating=0.0, director="", id="")

    def GetListMovies(self, request, context):
        for movie in self.db:
            yield movie_pb2.MovieData(title=movie['title'], rating=movie['rating'], director=movie['director'],
                                      id=movie['id'])

    def GetMovieByTitle(self, request, context):
        for movie in self.db:
            if movie["title"] == request.title:
                return movie_pb2.MovieData(title=movie["title"], rating=movie['rating'], director=movie['director'],
                                      id=movie['id'])
        return movie_pb2.MovieData(title="", rating=0.0, director="", id="")

    def CreateMovie(self, request, context):
        newMovie = {
            "id" : request.id,
            "title" : request.title,
            "rating" : request.rating,
            "director" : request.director
        }
        for movie in self.db:
            if movie["id"] == newMovie["id"]:
                return movie_pb2.NotificationMessage(message="Movie id already exist")
        self.db.append(newMovie)
        return movie_pb2.NotificationMessage(message="Movie added!")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    movie_pb2_grpc.add_MovieServicer_to_server(MovieServicer(), server)
    server.add_insecure_port('[::]:3001')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
