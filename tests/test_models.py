import asyncio
from typing import List, Callable, Coroutine, Any, Awaitable
from unittest import TestCase

import loguru
import ormar
import pytest
from model.models import User, database, Task
from routers.tasks_router import ScheduledNotifyTask


def rollback_operations(func):
    @pytest.mark.asyncio
    async def inner(event_loop):
        async with database:
            async with database.transaction(force_rollback=True):
                await func(event_loop)

    return inner


@pytest.fixture(autouse=True)
def start_up_fixture():
    asyncio.get_event_loop().run_until_complete(database.connect())
    yield
    asyncio.get_event_loop().run_until_complete(database.disconnect())


@rollback_operations
async def test_create_user(event_loop):
    user_new = await User.objects.create(per_hour_cost=220)
    user = await User.get_by_id(user_new.id)
    loguru.logger.info(user.id)
    assert user.per_hour_cost == 220


def test_filter_list():
    scheduled_notifications: List[ScheduledNotifyTask] = [ScheduledNotifyTask(None, 1, 2),
                                                          ScheduledNotifyTask(None, 2, 3)]

    task_asyncio: ScheduledNotifyTask = list(filter(lambda task:
                                                    task.task_db_id == 2, scheduled_notifications))[0]

    assert task_asyncio.task_db_id == 2


@rollback_operations
async def test_get_by_non_exist_id(event_loop):
    with pytest.raises(ormar.NoMatch):
        await User.get_by_id(64523)


@rollback_operations
async def test_get_tasks_user(event_loop):
    user = await User.objects.create(id=2222, per_hour_cost=0)
    task = await Task.objects.create(name='Test',
                                     description='Test',
                                     hardness=0,
                                     executor=user.pk)
    user = await User.objects.select_related('tasks').get(id=2222)
    assert user.tasks[0].name == 'Test'
