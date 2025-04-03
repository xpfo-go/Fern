import argparse
import asyncio

from dotenv import load_dotenv

from src.mcp.client import MCPClient

load_dotenv(dotenv_path='config/.env')


async def main():
    parser = argparse.ArgumentParser(description='Run Bonjour Service')
    parser.add_argument('--host', default='localhost', help='Host to bind to')
    parser.add_argument('--port', type=int, default=18080, help='Port to listen on')
    parser.add_argument('--debug', type=bool, default=False, help='Is debug')
    args = parser.parse_args()
    client = MCPClient()
    try:
        await client.connect_to_sse_server(args)
        #  这里阻塞
        await client.chat_loop()
    except KeyboardInterrupt:
        pass
    finally:
        await client.cleanup()

if __name__ == '__main__':
    asyncio.run(main())
