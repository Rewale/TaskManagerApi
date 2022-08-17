from typing import Callable

import loguru
from fastapi.testclient import TestClient
from main import app
from model import schemas
from model.db import database
from model.models import Task


def client_app(func: Callable[[TestClient], None]):
    def inner():
        with TestClient(app) as client:
            func(client)

    return inner


@client_app
def test_get_task(client: TestClient):
    response_task = client.post('/create_task', data=Task(executor=2222,
                                                          name='Test',
                                                          description='test',
                                                          hardness=2).json())
    assert response_task.status_code == 200

    response = client.get('/get_user?user_id=2222')
    assert response.status_code == 200
    assert response.json()['tasks'][0]
    assert 'taskreports' not in response.json()['tasks'][0]
    loguru.logger.info(response.json())


@client_app
def test_create_user(client: TestClient):
    response = client.post('/reg_user?user_id=2222')
    assert response.status_code == 200
    assert response.json()


@client_app
def test_create_task(client: TestClient):
    response = client.post('/create_task', data=schemas.Task(name='test', description='test',
                                                             hardness=0, executor=2222).json())
    loguru.logger.info(str(response.json()))
    assert response.status_code == 200
    task_id = response.json()['id']
    response_get_task = client.get(f'/get_task?task_id={task_id}')
    loguru.logger.info(str(response_get_task.json()))
    assert response_get_task.status_code == 200
    assert response_get_task.json()['name'] == 'test'

