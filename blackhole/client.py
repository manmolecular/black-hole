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
        extra: dict,
    ):
        """
        Initialize client handler for the client
        :param reader: stream reader for read
        :param writer: stream writer for write
        :param collector: data collector
        :param extra: extra parameters
        """
        peer_name = writer.get_extra_info("peername")
        self._client_id: str = ":".join(str(prop) for prop in peer_name)

        extra_name = extra.get("name")
        self.name = extra_name if extra_name else self.__class__.__name__
        self.name += f"/{self._client_id}"

        self._host = extra.get("host", "unknown")
        self._port = extra.get("port", 0)

        self._reader = reader
        self._writer = writer
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

            self._log.debug(
                "received data from client '%s' on the '%s' listener: %s",
                self._client_id,
                self.name,
                data,
            )

            try:
                await self._collector.add_record(
                    self._client_id, data, self._host, self._port
                )
            except Exception as err:  # noqa, pylint: disable=broad-exception-caught
                self._log.error(err)

            if delay is not None:
                await asyncio.sleep(delay)

            # Send empty data as response, imitate delay if required
            self._writer.write(b"")
            await self._writer.drain()
