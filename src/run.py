import argparse
import asyncio
import time

from src.mcp.client import MCPClient
from src.mcp.server import MCPServer
from src.tts.tts import TTS


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

    # start tts
    # tts = TTS()

    # --------------- core --------------------
    # 1. develop: test mcp client,mcp server
    # start mcp client console
    # await client.run_with_console()
    # await client.run_with_stream_console()

    # 2. develop: test llm to tts
    import pyttsx3
    engine = pyttsx3.init()
    while True:
        try:
            query = input(f"\n{client.Username}: ").strip()
            if query.lower() == 'quit':
                break
            if query == '':
                continue

            text = await client.process(query)
            print(f"\n菲伦: {text}")
            engine.say(text)
            engine.runAndWait()
            print(client.history_conversation)
        except Exception as e:
            print(f"\nError: {str(e)}")

