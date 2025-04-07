import argparse
import asyncio
import threading
import time
import logging

from src.mcp.client import MCPClient
from src.mcp.server import MCPServer
from src.stt.stt import STT
from src.tts.tts import TTS

for logger_name in [__name__, 'uvicorn', 'uvicorn.error', 'uvicorn.access', 'openai', 'requests', 'urllib3']:
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.WARNING)
    logger.addHandler(logging.FileHandler('logs/fern.log'))
    logger.propagate = False


async def run():
    parser = argparse.ArgumentParser(description='Run Fern Service')
    parser.add_argument('--host', default='localhost', help='Host to bind to')
    parser.add_argument('--port', type=int, default=18080, help='Port to listen on')
    parser.add_argument('--debug', type=bool, default=False, help='Is debug')
    parser.add_argument('--log_level', type=str, default='info', help='log level')
    args = parser.parse_args()

    # start mcp sse server
    server = MCPServer()
    await server.run_with_sync_sse(args.host, args.port, args.debug, args.log_level)

    # start mcp client and connect mcp sse server
    server_url = f'http://{args.host}:{args.port}/sse'
    client = MCPClient()
    await client.connect_to_mcp_sse_server(server_url)

    # system tts engine
    import pyttsx3
    engine = pyttsx3.init()

    # --------------- core --------------------
    # 1. develop: test mcp client,mcp server
    # start mcp client console
    # await client.run_with_console()
    await client.run_with_stream_console()

    # 2. develop: test llm to tts
    # while True:
    #     try:
    #         query = input(f"\n{client.Username}: ").strip()
    #         if query.lower() == 'quit':
    #             break
    #         if query == '':
    #             continue
    #
    #         text = await client.process(query)
    #         print(f"\n菲伦: {text}")
    #         engine.say(text)
    #         engine.runAndWait()
    #         print(client.history_conversation)
    #     except Exception as e:
    #         print(f"\nError: {str(e)}")

    # 3. stt llm tts
    # stt = STT()
    #
    # async def stt_async_callback(text):
    #     print(f"\n{client.Username}: {text}")
    #     response = await client.process(text)
    #     print(f"\n菲伦: {response}")
    #     engine.say(response)
    #     engine.runAndWait()
    #
    # def stt_sync_callback(text):
    #     print(text)
    #
    # 第一种方式：传入的是异步函数
    # stt.run_with_async_callback(stt_async_callback)
    # await asyncio.Future()
    #
    # 第二种方式：传入的是同步函数
    # stt.run_with_sync_callback(stt_sync_callback)
