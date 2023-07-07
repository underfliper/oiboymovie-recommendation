import os
import psycopg2
from dotenv import load_dotenv
from flask import Flask

from recommendations.by_movie import recommend_by_movie
from recommendations.by_user import recommend_by_user

load_dotenv()

app = Flask(__name__)
url = os.getenv("DATABASE_URL")
connection = psycopg2.connect(url)


@app.get("/recommendations/by-movie/<int:movie_id>")
def get_recommendations_by_movie(movie_id):
    return recommend_by_movie(connection, movie_id)


@app.get("/recommendations/by-user/<int:user_id>")
async def get_recommendations_by_user(user_id):
    return await recommend_by_user(connection, user_id)
