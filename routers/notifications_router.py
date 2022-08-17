import asyncio
from typing import List

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

from loggers.loggers import notification_logger
from model import schemas
from model.models import Task

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <h2>Your ID: <span id="ws-id"></span></h2>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var client_id = Date.now()
            document.querySelector("#ws-id").textContent = client_id;
            var ws = new WebSocket(`ws://localhost:8000/notification/ws/${client_id}`);
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    @staticmethod
    async def send_personal_message(message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

    async def send_task_notification_user(self, user_id: int, task: Task):
        notification_message = schemas.NotificationTaskWorking(user_id=user_id, task_id=task.id).json()
        await self.broadcast(message=notification_message)
        notification_logger.info(f'[NOTIFY_TASK] Отправлено сообщение {notification_message} всем пользователям')


notifications_router = APIRouter(prefix='/notification')
manager = ConnectionManager()


async def notify_task_task(task: Task, interval: int = 5):
    while True:
        notification_logger.info(f'[NOTIFY_TASK] Отправка пользователю {task.executor.id} задачи'
                                 f' {task.name} каждые {interval}')
        await asyncio.sleep(interval)
        await manager.send_task_notification_user(task.executor.id, task)


@notifications_router.websocket('/ws/{user_id}')
async def notification(websocket: WebSocket, user_id: int):
    await manager.connect(websocket)
    try:
        while True:
            _ = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@notifications_router.post('/send_task_notification/{user_id}')
async def send_notification(user_id: int, task: Task):
    await manager.send_task_notification_user(user_id, task)
    return schemas.StatusCode(message=task.dict())


@notifications_router.get("/test_notify_client")
async def get():
    return HTMLResponse(html)
