import requests as rq
from bs4 import BeautifulSoup as bs

HEADERS = {"User-Agent": "Mozilla/5.0"}

def scrape_movies() -> dict[int, str]:
    url = "https://www.csfd.cz/zebricky/filmy/nejlepsi/"
    args = [
        "",
        "?from=100",
        "?from=200",
        "?from=300"
    ]

    # id, name
    movies = {}

    for arg in args:
        resp = rq.get(url + arg, headers=HEADERS)
        resp.raise_for_status()
        html = resp.text
        soup = bs(html, "html.parser")
        tags = soup.find_all("h3", attrs={"class": "film-title-norating"})

        for tag in tags:
            if tag.find("span").text.strip() == "301.":
                break
            anchor = tag.find("a")
            link = anchor.get("href")
            movie_id = int(link[6:link.find("-")])
            movies[movie_id] = anchor.get("title").strip()

    return movies

def scrape_data() -> dict[str, dict]:
    MOVIE_ENDPOINT_URL = "https://csfd.cz/film/"
    data = {
        "actor": {},
        "movie": {},
        "actor_movie": []
    }

    data["movie"] = scrape_movies()

    for movie_id in data["movie"].keys():
        resp = rq.get(MOVIE_ENDPOINT_URL + str(movie_id), headers=HEADERS)
        resp.raise_for_status()
        html = resp.text
        soup = bs(html, "html.parser")

        div_creators = soup.find("div", attrs={"class": "creators"})
        div_actors = None
        for div in div_creators.find_all("div"):
            if div.find("h4").text.strip() == "Hrají:":
                div_actors = div

        actor_anchors = div_actors.find_all("a")

        for actor in actor_anchors:
            link = actor.get("href")
            if link == "#":
                continue
            actor_id = link[8:link.find("-")]
            actor_name = actor.text.strip()

            data["actor"][actor_id] = actor_name
            data["actor_movie"].append((actor_id, movie_id))
    
    return data
