from pydantic import BaseModel
from typing import Optional, List, Dict, Any, Union
import datetime


class LineResponse(BaseModel):
    line_id: int
    image_path: Optional[str]
    line_fullname:Optional[str]
