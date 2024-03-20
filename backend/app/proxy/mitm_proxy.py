import asyncio
import websockets
import logging
from Crypto.Cipher import AES
import base64
import json

# Настройка логгера
logging.basicConfig(filename='proxy_logs.txt', filemode='w', level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger()

def decrypt_aes_ecb(encrypted_message, key):
    cipher = AES.new(key, AES.MODE_ECB)
    decrypted_message = cipher.decrypt(base64.b64decode(encrypted_message))
    # Правильное удаление паддинга для сообщений, дополненных до размера блока AES
    return decrypted_message.rstrip(b"\x00").decode()

async def handler(websocket, path):
    async with websockets.connect('ws://localhost:8000/ws/') as server_websocket:
        logger.info("Proxy connected to server and client")
        try:
            while True:
                client_message = await websocket.recv()
                logger.info(f"Received from client: {client_message}")
                await server_websocket.send(client_message)

                server_response = await server_websocket.recv()
                logger.info(f"Received from server: {server_response}")

                # Попытка расшифровать перехваченное сообщение от сервера
                try:
                    response_data = json.loads(server_response)
                    if 'data' in response_data and 'message' in response_data['data']:
                        encrypted_message = response_data['data']['message']
                        # Замените 'your_key_here' на ваш фактический ключ шифрования
                        key = b"thisisabadkey123"
                        decrypted_message = decrypt_aes_ecb(encrypted_message, key)
                        logger.info(f"Decrypted message: {decrypted_message}")
                        # Можно опционально модифицировать ответ сервера, чтобы отобразить расшифрованное сообщение
                        # response_data['data']['message'] = decrypted_message
                        # server_response = json.dumps(response_data)
                except Exception as e:
                    logger.error(f"Error decrypting message: {e}")

                await websocket.send(server_response)
        except websockets.exceptions.ConnectionClosed as e:
            logger.info(f"Connection closed: {e}")

start_server = websockets.serve(handler, "localhost", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()


# cd /root_app/backend/app/proxy
# python mitm_proxy.py
