import asyncio
import json
import websockets
import pytest

from common.app.db.api_db import clear_db
from common.app.db.db_pool import init_pool
from common.app.core.config import config as cfg_c
from Crypto.Cipher import AES
import base64


def pad(s):
    return s + (AES.block_size - len(s) % AES.block_size) * chr(AES.block_size - len(s) % AES.block_size)


def encrypt_aes_ecb(message: str, key):
    message = pad(message)
    cipher = AES.new(key, AES.MODE_ECB)
    encrypted_message = cipher.encrypt(message.encode())
    return base64.b64encode(encrypted_message).decode()


# Генерация фиксированного ключа для демонстрации
key = b"thisisabadkey123"  # Ключ должен быть размером 16 (AES-128), 24 (AES-192) или 32 (AES-256) байта


# cd /root_app/backend/app/tests
# pytest send_messages_test.py
async def send_and_receive(websocket, message, expected_responses_count, timeout=3):
    print(f"Отправлено на сервер: {message}")
    await websocket.send(message)

    responses = []
    start_time = asyncio.get_event_loop().time()

    while len(responses) < expected_responses_count and asyncio.get_event_loop().time() - start_time < timeout:
        try:
            response = await asyncio.wait_for(websocket.recv(), timeout=timeout)
            responses.append(json.loads(response))
            print(f"Received from server: {response}")
        except asyncio.TimeoutError:
            print("Превышено время ожидания ответа от сервера")
            break

    return responses


async def send_messages_and_get_all():
    uri = "ws://localhost:8765/ws/"
    async with websockets.connect(uri) as websocket:
        # Шифрование и отправка сообщения
        encrypted_message = encrypt_aes_ecb("Hello WebSocket!", key)
        message = {"type": "send", "message": encrypted_message}
        await send_and_receive(websocket, json.dumps(message), 1)

        # Шифрование и отправка второго сообщения
        encrypted_message = encrypt_aes_ecb("Second Message", key)
        message = {"type": "send", "message": encrypted_message}
        await send_and_receive(websocket, json.dumps(message), 1)

        # Запрашиваем все сообщения
        request_all_messages = {"type": "get_all"}
        responses = await send_and_receive(websocket, json.dumps(request_all_messages), 1)

    print(f"responses: {responses}")


@pytest.mark.asyncio
async def test_send_and_receive_messages():
    await init_pool(cfg=cfg_c)
    await clear_db()
    await send_messages_and_get_all()
