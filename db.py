from fastapi import FastAPI, Depends
from typing import Annotated
import psycopg
from psycopg.rows import dict_row

app = FastAPI()

import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def get_db():
    with psycopg.connect(DATABASE_URL, row_factory=dict_row) as conn:
        yield conn

DB = Annotated[psycopg.Connection, Depends(get_db)]