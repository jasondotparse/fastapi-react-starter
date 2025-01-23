# schemas.py
from pydantic import BaseModel
from typing import Optional, Dict, Literal, Union, Annotated
from pydantic import Field


class UserSchema(BaseModel):
    username: str
    age: int
    
class UserRespSchema(BaseModel):
    id: int
    username: str
    age: int