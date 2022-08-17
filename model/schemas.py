from datetime import datetime
from enum import Enum
from typing import Union, Optional, List

from pydantic import BaseModel, validator

from model import models


class NotificationEnum(Enum):
    TASK_WORK = 1


class StatusEnum(Enum):
    OK = 'ok'
    ERROR = 'error'


class StatusCode(BaseModel):
    status: StatusEnum = StatusEnum.OK
    message: Union[str, dict]


class NotificationTaskWorking(BaseModel):
    user_id: int
    task_id: int


class Task(BaseModel):
    class Config:
        orm_mode = True

    id: Optional[int]
    executor: Optional[int]
    name: str
    description: str
    hardness: int
    time_create: Optional[datetime]

    @validator('executor', pre=True)
    def set_executor(cls, executor):
        if isinstance(executor, dict):
            return executor['id']
        else:
            return executor


class User(BaseModel):
    class Config:
        orm_mode = True

    id: int
    tasks: Optional[List[Task]]
