import os

import psycopg
from dotenv import load_dotenv


load_dotenv()


def get_connection():
    return psycopg.connect(
        host="localhost",
        port=5432,
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
    )