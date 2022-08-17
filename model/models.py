import datetime
from typing import Optional, Union, Dict, List

import ormar

from .db import metadata, database, engine


class MainMeta(ormar.ModelMeta):
    metadata = metadata
    database = database


class User(ormar.Model):
    class Meta(MainMeta):
        pass

    id: int = ormar.Integer(primary_key=True)
    per_hour_cost: int = ormar.Integer()

    @classmethod
    async def get_by_id(cls, user_id) -> 'User':
        user = await User.objects.select_related('tasks').get(id=user_id)
        return user

    @classmethod
    async def get_user_tasks(cls, user_id) -> List['Task']:
        user = await User.get_by_id(user_id)
        return user.tasks


class Task(ormar.Model):
    class Meta(MainMeta):
        pass

    id: int = ormar.Integer(primary_key=True)
    name: str = ormar.String(max_length=50)
    description: str = ormar.String(max_length=1000)
    hardness: int = ormar.Integer()
    time_create: datetime.datetime = ormar.DateTime(default=datetime.datetime.now)
    executor: Optional[Union[User, Dict, int]] = ormar.ForeignKey(User, related_name='tasks')
    is_execute: bool = ormar.Boolean(default=False)

    async def set_executor(self, user: User):
        self.executor = user
        await self.update()

    async def stop_execute(self):
        self.is_execute = False
        await self.update()

    async def start_execute(self):
        self.is_execute = True
        await self.update()

    @classmethod
    async def get_by_id(cls, task_id):
        return await Task.objects.get(id=task_id)


class TaskReport(ormar.Model):
    class Meta(MainMeta):
        pass

    task_id: Task = ormar.ForeignKey(to=Task)
    report_id: int = ormar.Integer(primary_key=True, autoincrement=True)

    text: str = ormar.String(max_length=1000)
    time_create = ormar.DateTime(default=datetime.datetime.now)
    automatically: bool = ormar.Boolean(default=False)
