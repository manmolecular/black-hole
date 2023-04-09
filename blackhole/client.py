"""Module provides client handlers"""
# pylint: disable=too-few-public-methods
import asyncio
import logging
from typing import Union

from blackhole.collector import Collector


class ClientHandler:  # noqa, pylint: disable=too-many-instance-attributes
    """
    Class handles interaction process with the client using reader/writer streams
    """

    def __init__(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
        collector: Collector,
        *,
        name: Union[None, str] = None,
    ):
        """
        Initialize client handler for the client
        :param reader: stream reader for read
        :param writer: stream writer for write
        :param collector: data collector
        :param name: internal name of the instance (optional)
        """
        self.name = name if name else self.__class__.__name__

        self._reader = reader
        self._writer = writer

        self._peer_name = writer.get_extra_info("peername")
        self._client_id: str = ":".join(str(prop) for prop in self._peer_name)

        self._collector = collector

        self._log = logging.getLogger(self.name)
        self._log.debug(
            "initialize client listener '%s' for client '%s'",
            self.name,
            self._client_id,
        )

    async def handle(self, read_size: int, delay: Union[None, float]) -> None:
        """
        Handle client interaction
        :param read_size: number of bytes to read from reader stream
        :param delay: add delay (in seconds) before response
        :return: None
        """
        while True:
            data = await self._reader.read(read_size)
            if not data:
                self._log.debug(
                    "client '%s' is disconnected from the '%s' listener",
                    self._client_id,
                    self.name,
                )

                return

            try:
                await self._collector.add_record(self._client_id, data, "", 0)
            except Exception as exc:  # noqa, pylint: disable=broad-exception-caught
                self._log.error(exc)

            self._log.debug(
                "received data from client '%s' on the '%s' listener: %s",
                self._client_id,
                self.name,
                data,
            )

            if delay is not None:
                await asyncio.sleep(delay)

            self._writer.write(b"")
            await self._writer.drain()
