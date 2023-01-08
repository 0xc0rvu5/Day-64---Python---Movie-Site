import os, requests
from tmdbv3api import TMDb
from tmdbv3api import Movie


TMDB_API_KEY = os.getenv('MOVIESDB_V3')
tmdb = TMDb()
tmdb.api_key = TMDB_API_KEY

MOVIE_DB_SEARCH_URL = "https://api.themoviedb.org/3/search/movie"
MOVIE_DB_API_KEY = TMDB_API_KEY


# movie_title = 'Mad Max'
# response = requests.get(MOVIE_DB_SEARCH_URL, params={"api_key": MOVIE_DB_API_KEY, "query": movie_title})
# data = response.json()['results']
# print(data)

movie = Movie()

m = movie.details(343611)

print(m.title)
print(m.poster_path)
print(m.vote_average)