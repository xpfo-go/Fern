import asyncio

from dotenv import load_dotenv

from src.run import run

load_dotenv(dotenv_path='config/.env')

if __name__ == '__main__':
    asyncio.run(run())
