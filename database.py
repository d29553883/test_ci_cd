from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os, sys
import logging
import pymysql

app = FastAPI()

load_dotenv()

DB_MASTER_USERNAME = os.getenv("RDS_USERNAME")
DB_MASTER_PASSWORD = os.getenv("RDS_PASSWORD")
DB_MASTER_HOST = os.getenv("RDS_HOSTNAME")
DB_MASTER_PORT = os.getenv("RDS_PORT")
DB_MASTER_NAME = os.getenv("RDS_DB_NAME")


DB_MASTER_ADDR = (
    "mysql+pymysql://"
    + DB_MASTER_USERNAME
    + ":"
    + DB_MASTER_PASSWORD
    + "@"
    + DB_MASTER_HOST
    + ":"
    + DB_MASTER_PORT
    + "/"
    + DB_MASTER_NAME
    + "?charset=utf8mb4"
)


try:
    master = create_engine(
        DB_MASTER_ADDR,
        connect_args={"connect_timeout": 5},
        convert_unicode=True,
        max_overflow=10,
        pool_size=50,
        pool_timeout=30,
        pool_recycle=600,
        pool_pre_ping=True,
    )

    SRead = sessionmaker(autocommit=False, autoflush=False, bind=master)
    SWrite = sessionmaker(autocommit=False, autoflush=False, bind=master)
    Base = declarative_base()
except:
    logging.exception("Catch an exception.")
