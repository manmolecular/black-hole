"""Module provides port listener functionality"""
import asyncio
import logging
from asyncio import Server
from typing import Union

from blackhole.client import ClientHandler
from blackhole.collector import Collector


class PortListener:  # noqa, pylint: disable=too-many-instance-attributes
    """
    Class implements port listener; for each client new handler is created
    """

    def __init__(
        self,
        host: str,
        port: int,
        collector: Collector,
        *,
        read_size: int = 1_024,
        delay: Union[None, float] = None,
        name: Union[None, str] = None,
    ):
        """
        Initialize port listener
        :param host: host to listen on
        :param port: port to listen on
        :param collector: data collector
        :param read_size: socket read size
        :param delay: add delay (in seconds) before response
        :param name: internal name of the instance
        """
        self.name = name if name else self.__class__.__name__
        self.name += f"/{port}"

        self.host = host
        self.port = port
        self.read_size = read_size
        self.delay = delay

        self._collector = collector

        self._server: Union[None, Server] = None

        self._log = logging.getLogger(self.name)
        self._log.debug(
            "initialize port listener '%s' on host '%s', port '%d'",
            self.name,
            self.host,
            self.port,
        )
        self._log.debug(
            "extra parameters for '%s': read_size=%d bytes, delay=%f seconds",
            self.name,
            self.read_size,
            self.delay,
        )

    async def _start_server(self, collector: Collector):
        """
        Internal method to assign new client handler instances after server start
        :param collector: data collector
        :return: None; internal assignment
        """

        def assign_handler(
            reader: asyncio.StreamReader, writer: asyncio.StreamWriter
        ) -> None:
            """
            Callback on new client connection
            :param reader: stream reader as data stream
            :param writer: stream writer as data stream
            :return: None
            """
            self._log.debug("new client is connected, initiate listener creation")
            listener = ClientHandler(
                reader,
                writer,
                collector,
                extra={
                    "host": self.host,
                    "port": self.port,
                },
            )

            task_handle = listener.handle(self.read_size, self.delay)

            asyncio.create_task(task_handle)

        self._server = await asyncio.start_server(
            assign_handler,
            self.host,
            self.port,
        )

    async def serve_forever(self) -> None:
        """
        Start server, assign handlers and serve_to_csv it forever
        :return: awaitable as 'serve_forever', None otherwise
        """
        try:
            await self._start_server(self._collector)
        except PermissionError:
            self._log.warning(
                "can not start server on host '%s', port '%d' - permission error",
                self.host,
                self.port,
            )

            return None
        except OSError:
            self._log.warning(
                "can not start server on host '%s', port '%d' - address already in use",
                self.host,
                self.port,
            )

            return None

        if isinstance(self._server, Server):
            await self._server.serve_forever()

    async def close(self) -> None:
        """
        Initiate the server closing, wait for it to finish
        :return: None
        """
        if isinstance(self._server, Server):
            self._server.close()
            self._log.debug(
                "close the server on host '%s', port '%d'", self.host, self.port
            )

            await self._server.wait_closed()
            self._log.debug(
                "successfully closed server on host '%s', port '%d'",
                self.host,
                self.port,
            )
