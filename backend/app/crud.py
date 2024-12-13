from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from sqlalchemy import func
from datetime import datetime
from fastapi import HTTPException
import json
from typing import Optional, List, Dict, Any, Union
import datetime as dt
import logging
import math


def convert_result(res):
    return [{c: getattr(r, c) for c in res.keys()} for r in res]


# def get_data(db: Session):
#     stmt = f"""
#         SELECT * FROM data_counter
#     """
#     try:
#         result = db.execute(text(stmt)).mappings().all()
#         return result
#     except Exception as e:
#         raise HTTPException(400,"Error get data :"+str(e))


def get_line(db: Session):
    stmt = f"""
        SELECT b.line_id, b.image_path ,c.line_fullname
        FROM public.image_path_screenshot b
        JOIN line c on b.line_id = c.line_id
    """
    try:
        result = db.execute(text(stmt)).mappings().all()
        return result
    except Exception as e:
        raise HTTPException(400, "Error get section :" + str(e))
