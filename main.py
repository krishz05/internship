from fastapi import FastAPI, Query
from typing import Optional, List
import configparser
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

# Load config
config = configparser.ConfigParser()
config.read('config.ini')

# Parse options
languages = [lang.strip() for lang in config['LANGUAGES']['available'].split(',')]
genres = [g.strip() for g in config['GENRES']['available'].split(',')]
subtitles = [s.strip() for s in config['SUBTITLES']['available'].split(',')]

# Parse movies
movie_lines = config['MOVIES']['movies'].strip().split('\n')
movies_db = []

for line in movie_lines:
    name, lang, genre, subtitle = [part.strip() for part in line.split('|')]
    movies_db.append({
        "name": name,
        "language": lang,
        "genre": genre,
        "subtitle": subtitle
    })

from fastapi import HTTPException

@app.get("/movies")
def get_movies(
    name: Optional[str] = Query(None),
    language: Optional[str] = Query(None),
    genre: Optional[str] = Query(None),
    subtitle: Optional[str] = Query(None)
):
    # Validate inputs if given
    if language and language not in languages:
        raise HTTPException(status_code=404, detail=f"Language '{language}' is not supported.")
    if genre and genre not in genres:
        raise HTTPException(status_code=404, detail=f"Genre '{genre}' is not supported.")
    if subtitle and subtitle not in subtitles:
        raise HTTPException(status_code=404, detail=f"Subtitle option '{subtitle}' is not available.")

    filtered = movies_db

    if name:
        matched_movies = [m for m in filtered if m['name'].lower() == name.lower()]
        if not matched_movies:
            raise HTTPException(status_code=404, detail=f"Movie '{name}' not found.")
        filtered = matched_movies

    if language:
        filtered = [m for m in filtered if m['language'] == language]
    if genre:
        filtered = [m for m in filtered if m['genre'] == genre]
    if subtitle:
        filtered = [m for m in filtered if m['subtitle'] == subtitle]

    if not filtered:
        raise HTTPException(status_code=404, detail="No movies found matching the given filters.")

    return {
        "filters_applied": {
            "name": name,
            "language": language,
            "genre": genre,
            "subtitle": subtitle
        },
        "results": filtered
    }


# Allow React frontend on localhost:3000
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
