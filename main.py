from contextlib import asynccontextmanager
from unidecode import unidecode

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from app.scraping import scrape_data
from app.db_handling import get_session, fill_the_database, is_empty, search_query, get_actors_by_movie, get_movies_by_actor

@asynccontextmanager
async def lifespan(app: FastAPI):
    with get_session() as session:
        if is_empty(session):
            data = scrape_data()
            fill_the_database(session, data)
    yield
    print("Shutdown...")


app = FastAPI(lifespan=lifespan)

@app.get("/", response_class=HTMLResponse)
async def index():
    with open("./static/app.html", "r") as FILE:
        return FILE.read()
    
@app.get("/search")
async def search(query: str):
    result = {"actors": {}, "movies": {}}

    if len(query) < 3:
        return result

    translittered_query = unidecode(query).lower()
    
    with get_session() as session:
        actors, movies = search_query(session, translittered_query)
        result["actors"] = {actor.id: actor.name for actor in actors}
        result["movies"] = {movie.id: movie.name for movie in movies}
    
    return result

@app.get("/api/movies/{movie_id}")
async def movie_detail(movie_id: int):
    result = {}

    with get_session() as session:
        actors = get_actors_by_movie(session, movie_id)
        result = {actor.id: actor.name for actor in actors}

    return result

@app.get("/api/actors/{actor_id}")
async def actor_detail(actor_id: int):
    result = {}

    with get_session() as session:
        movies = get_movies_by_actor(session, actor_id)
        result = {movie.id: movie.name for movie in movies}

    return result

