import asyncio
import logging
from sentinel.worker.worker import run_worker

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    asyncio.run(run_worker())
