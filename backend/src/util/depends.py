

import asyncio


async def check_periodically(task, sleep_time: int = 5):
    while True:
        await task()
        await asyncio.sleep(sleep_time)
