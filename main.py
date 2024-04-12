import asyncio
import logging
import re

import websockets

SOCKET_URL = 'wss://www.apex-timing.com:8913/'
FILE_NAME = 'best_lap_time.txt'

logging.basicConfig(format='%(message)s')
logger = logging.getLogger("APP")
logger.setLevel(logging.INFO)


def save_best_lap_time(best_lap_time: float):
    with open(FILE_NAME, "w") as file:
        file.write(str(best_lap_time))


def load_best_lap_time():
    try:
        with open(FILE_NAME, "r") as file:
            content = file.read()
            if not content:
                return None
            best_lap_time = float(content)
            logger.info("LOADED BEST LAP TIME: %s", best_lap_time)
            return best_lap_time
    except FileNotFoundError:
        return None


async def main():
    logger.info("STARTED LISTENING FOR BEST LAP TIMES")
    best_lap_time = load_best_lap_time()
    async with websockets.connect(SOCKET_URL) as websocket:
        while True:
            response = await websocket.recv()
            match = re.search(r'r\d+c11\|ib\|([+-]?([0-9]*[.])?[0-9]+)', response)
            if match:
                lap_time = float(match.group(1))

                if not best_lap_time:
                    best_lap_time = lap_time
                    save_best_lap_time(best_lap_time)
                    logger.info("INITIAL BEST LAP TIME: %s", best_lap_time)
                    continue

                if lap_time < best_lap_time:
                    best_lap_time = lap_time
                    save_best_lap_time(best_lap_time)
                    logger.info("NEW BEST LAP TIME: %s", best_lap_time)


if __name__ == '__main__':
    asyncio.run(main())
