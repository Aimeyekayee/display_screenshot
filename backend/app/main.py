from PIL import Image
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from apscheduler.schedulers.blocking import BlockingScheduler
import logging
import os
import time
from . import crud
import datetime as dt
from fastapi import Depends, FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .database import SessionLocal, engine
from typing import Union, List
import uvicorn

from .schemas import LineResponse


origins = ["*"]

app = FastAPI()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get("/get_line", response_model=List[LineResponse])
async def get_line(db: Session = Depends(get_db)):
    section = crud.get_line(db=db)
    return section
