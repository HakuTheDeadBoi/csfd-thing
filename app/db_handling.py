from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from unidecode import unidecode

from contextlib import contextmanager

Base = declarative_base()
engine = create_engine('sqlite:///.database.db')
Session = sessionmaker(bind=engine)

class Actor(Base):
    __tablename__ = "actor"
    id = Column(Integer, primary_key=True)
    name = Column(String)

class Movie(Base):
    __tablename__ = "movie"
    id = Column(Integer, primary_key=True)
    name = Column(String)

class ActorMovie(Base):
    __tablename__ = "actor_movie"
    actor_id = Column(Integer, ForeignKey("actor.id"), primary_key=True)
    movie_id = Column(Integer, ForeignKey("movie.id"), primary_key=True)

Base.metadata.create_all(bind=engine)

@contextmanager
def get_session():
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()

def fill_the_database(session: Session, data: dict[str, str]) -> None:
    for actor_id, actor_name in data["actor"].items():
        new_actor = Actor(id=actor_id, name=actor_name)
        session.add(new_actor)

    for movie_id, movie_name in data["movie"].items():
        new_movie = Movie(id=movie_id, name=movie_name)
        session.add(new_movie)

    for actor_id, movie_id in data["actor_movie"]:
        new_actor_movie = ActorMovie(actor_id=actor_id, movie_id=movie_id)
        session.add(new_actor_movie)

def is_empty(session: Session) -> bool:
    return session.query(Actor).count() == 0 and session.query(Movie).count() == 0 and session.query(ActorMovie).count() == 0

def search_query(session: Session, q: str):
    actors = session.query(Actor).order_by(Actor.name).all()
    movies = session.query(Movie).order_by(Movie.name).all()

    matching_actors = [actor for actor in actors if q in unidecode(actor.name).lower()]
    matching_movies = [movie for movie in movies if q in unidecode(movie.name).lower()]

    return (matching_actors, matching_movies)

def get_movies_by_actor(session: Session, actor_id: int):
    movies = session.query(Movie).join(ActorMovie).filter(ActorMovie.actor_id == actor_id).order_by(Movie.name).all()
    return movies

def get_actors_by_movie(session: Session, movie_id: int):
    actors = session.query(Actor).join(ActorMovie).filter(ActorMovie.movie_id == movie_id).order_by(Actor.name).all()
    return actors





