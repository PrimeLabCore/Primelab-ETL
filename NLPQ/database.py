import os
import pandas as pd
from sqlalchemy import create_engine  # type: ignore
from sqlalchemy.ext.declarative import declarative_base  # type: ignore
from sqlalchemy.orm import sessionmaker  # type: ignore
from typing_extensions import TypedDict

from sqlalchemy import Column, Integer, String  # type: ignore
# host = os.environ["POSTGRES_HOST"]
# port = os.environ["POSTGRES_PORT"]
# user = os.environ["POSTGRES_USER"]
# password = os.environ["POSTGRES_PASS"]
# db = os.environ["POSTGRES_DB"]
# dbtype = "postgresql"

SQLALCHEMY_DATABASE_URI = "" #add your db here

engine = create_engine(SQLALCHEMY_DATABASE_URI)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
