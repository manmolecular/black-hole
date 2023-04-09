"""Module provides core wrapper and functionality"""
import asyncio
from typing import Iterable

import aiofiles

from blackhole.collector import CsvTypeCollector, Collector, StdoutTypeCollector
from blackhole.port import PortListener


async def serve(
    host: str, ports: Iterable[int], collector: Collector, *args, **kwargs
) -> None:
    """
    Start server
    :param host: host to listen oon
    :param ports: ports to listen on
    :param collector: collector to save data to
    :param args: additional args
    :param kwargs: additional kwargs
    :return: None
    """
    listeners = (PortListener(host, port, collector, *args, **kwargs) for port in ports)

    tasks = (listener.serve_forever() for listener in listeners)

    try:
        await asyncio.gather(*tasks)
    except KeyboardInterrupt:  # gracefully close listeners
        for listener in listeners:
            await listener.close()


async def serve_to_stdout(host: str, ports: Iterable[int], *args, **kwargs) -> None:
    """
    Start server and log data to stdout
    :param host: host to listen on
    :param ports: ports to listen on
    :param args: additional args
    :param kwargs: additional kwargs
    :return: None
    """
    collector = StdoutTypeCollector()

    await serve(host, ports, collector, *args, **kwargs)


async def serve_to_csv(
    host: str, ports: Iterable[int], filename: str, *args, **kwargs
) -> None:
    """
    Start server and save data to csv
    :param host: host to listen on
    :param ports: ports to listen on
    :param filename: name of the file to write to
    :param args: additional args
    :param kwargs: additional kwargs
    :return: None
    """
    async with aiofiles.open(filename, mode="w", encoding="utf-8") as afp:
        collector = CsvTypeCollector(afp)
        await collector.prepare()

        await serve(host, ports, collector, *args, **kwargs)
