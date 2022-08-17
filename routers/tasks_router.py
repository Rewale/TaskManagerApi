import asyncio
import datetime
import sqlite3
import traceback
from dataclasses import dataclass
from typing import List, Union

import ormar
from fastapi import APIRouter

from model import schemas
from model.models import User, Task, TaskReport
from model.schemas import StatusCode, StatusEnum
from routers.notifications_router import notify_task_task

tasks_router = APIRouter()


@dataclass
class ScheduledNotifyTask:
    asyncio_task: asyncio.tasks.Task
    task_db_id: int
    user_id: int


scheduled_notifications: List[ScheduledNotifyTask] = []


@tasks_router.post('/create_user')
async def create_user(user: User):
    try:
        return await user.save()
    except sqlite3.IntegrityError:
        return StatusCode(status=StatusEnum.ERROR, message='Пользователь уже существует')


@tasks_router.post('/reg_user', response_model=schemas.User)
async def create_user(user_id: int):
    try:
        return await User(id=user_id, per_hour_cost=0).save()
    except sqlite3.IntegrityError:
        return StatusCode(status=StatusEnum.ERROR, message='Пользователь уже существует')


@tasks_router.post('/create_task', response_model=schemas.Task)
async def create_task(task: schemas.Task):
    try:
        task.time_create = task.time_create or datetime.datetime.now()
        return await Task(**task.dict()).save()
    except sqlite3.IntegrityError as e:
        return StatusCode(status=StatusEnum.ERROR, message=f'Задача уже создана: {e}')


@tasks_router.get('/get_task', response_model=schemas.Task)
async def get_task(task_id: int) -> Union[User, StatusCode, None]:
    try:
        return await Task.get_by_id(task_id)
    except ormar.NoMatch:
        return None
    except Exception as e:
        return StatusCode(status=StatusEnum.ERROR, message=f'{e}')


# response_model_exclude={"tasks__taskreports"} - как вариант можно убирать поля вложенных сущностей
@tasks_router.get('/get_user', response_model=schemas.User)
async def get_user(user_id: int) -> Union[User, StatusCode, None]:
    try:
        return await User.get_by_id(user_id)
    except ormar.NoMatch:
        return None
    except Exception as e:
        return StatusCode(status=StatusEnum.ERROR, message=f'{e}')


@tasks_router.get('/get_user_task', response_model=List[schemas.Task])
async def get_user_task(user_id: int):
    return await User.get_user_tasks(user_id)


@tasks_router.post('/start_task')
async def accept_task(task_id: int):
    task = await Task.objects.get(id=task_id)
    await task.start_execute()
    scheduled_task = asyncio.create_task(notify_task_task(task))
    notify_task = ScheduledNotifyTask(asyncio_task=scheduled_task, task_db_id=task_id, user_id=task.executor.id)
    scheduled_notifications.append(notify_task)


@tasks_router.post('/cancel_task')
async def cancel_task(task_report: TaskReport):
    await task_report.save()
    task = await Task.get_by_id(task_report.task_id)
    await task.stop_execute()
    task_id = task_report.task_id.id
    task_asyncio: ScheduledNotifyTask = list(filter(lambda task_inner: task_inner.task_db_id == task_id,
                                                    scheduled_notifications))[0]
    task_asyncio.asyncio_task.cancel()
