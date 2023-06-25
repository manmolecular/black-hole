"""Module provides core wrapper and functionality"""
import asyncio
from typing import Iterable

import aiofiles

from blackhole.collector import CsvTypeCollector, Collector, StdoutTypeCollector
from blackhole.port import PortListener


class Server:
    """Implement manager-like instance to serve port listeners"""

    def __init__(self, host: str, ports: Iterable[int]):
        """
        Init server
        :param host: host to listen on
        :param ports: ports to listen on
        """
        self.host = host
        self.ports = ports
        self.listeners: Iterable[PortListener] = ()

    async def serve(self, collector: Collector, *args, **kwargs) -> None:
        """
        Start server
        :param collector: collector to save data to
        :param args: additional args for PortListener
        :param kwargs: additional kwargs for PortListener
        :return: None
        """
        self.listeners = tuple(
            PortListener(self.host, port, collector, *args, **kwargs)
            for port in self.ports
        )

        tasks = (listener.serve_forever() for listener in self.listeners)

        await asyncio.gather(*tasks)

    async def stop(self):
        """
        Gracefully stop the server
        :return: None
        """
        for listener in self.listeners:
            await listener.close()

    async def serve_to_stdout(self, *args, **kwargs) -> None:
        """
        Start server and log data to stdout
        :param args: additional args for PortListener
        :param kwargs: additional kwargs for PortListener
        :return: None
        """
        collector = StdoutTypeCollector()

        await self.serve(collector, *args, **kwargs)

    async def serve_to_csv(self, filename: str, *args, **kwargs) -> None:
        """
        Start server and save data to csv
        :param filename: name of the file to write to
        :param args: additional args for PortListener
        :param kwargs: additional kwargs for PortListener
        :return: None
        """
        async with aiofiles.open(filename, mode="w", encoding="utf-8") as afp:
            collector = CsvTypeCollector(afp)
            await collector.prepare()

            await self.serve(collector, *args, **kwargs)
