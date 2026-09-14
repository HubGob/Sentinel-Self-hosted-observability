import asyncio
import logging

from apps.worker.worker import run_worker

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    asyncio.run(run_worker())
