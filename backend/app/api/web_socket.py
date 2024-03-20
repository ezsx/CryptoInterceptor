import datetime
import json
import starlette

from datetime import datetime
from common.app.db.api_db import save_message, get_all_messages
from fastapi import FastAPI, WebSocket
from fastapi.websockets import WebSocketDisconnect

app_ws = FastAPI()


def datetime_handler(x):
    if isinstance(x, datetime):
        return x.isoformat()
    raise TypeError("Unknown type")


@app_ws.websocket("/")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)

            if message_data['type'] == 'send':
                # Сохраняем сообщение в базе данных
                saved_message = await save_message(message_data['message'])
                if saved_message:
                    saved_message["created_at"] = saved_message["created_at"].isoformat()
                await websocket.send_text(
                    json.dumps({"response": "Message saved", "data": saved_message}, default=datetime_handler))
                print(f"Server received: {message_data['message']}")



            elif message_data['type'] == 'get_all':

                # Получаем все сообщения, преобразуем datetime и отправляем их клиенту

                messages = await get_all_messages()

                for message in messages:
                    message["created_at"] = message["created_at"].isoformat()

                await websocket.send_text(
                    json.dumps({"response": "All messages", "messages": messages}, default=datetime_handler))
                print(f"Server sent: {messages}")

    except WebSocketDisconnect or starlette.websockets.WebSocketDisconnect:
        print("WebSocket disconnected")
