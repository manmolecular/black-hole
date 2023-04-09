"""Module provides core wrapper and functionality"""
import asyncio
import logging
from typing import Iterable

import aiofiles

from blackhole.collector import CsvTypeCollector
from blackhole.port import PortListener

# Suppress asyncio logging; allow only 'FATAL' messages
logging.getLogger("asyncio").setLevel(logging.FATAL)

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

DEFAULT_HOST = "127.0.0.1"

DEFAULT_PORTS = (
    21,
    22,
    23,
    25,
    53,
    80,
    110,
    111,
    135,
    139,
    143,
    443,
    445,
    993,
    995,
    1723,
    3306,
    3389,
    5900,
    8080,
)


async def serve(host: str = DEFAULT_HOST, ports: Iterable[int] = DEFAULT_PORTS):
    """
    Setup listeners and serve
    :return: None
    """
    async with aiofiles.open("output.csv", mode="w", encoding="utf-8") as afp:
        collector = CsvTypeCollector(afp)
        await collector.prepare()

        listeners = (PortListener(host, port, collector) for port in ports)

        tasks = (listener.serve_forever() for listener in listeners)

        try:
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:  # gracefully close listeners
            for listener in listeners:
                await listener.close()
