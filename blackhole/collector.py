"""Module provides collecting interfaces and implementations"""
# pylint: disable=too-many-arguments
import logging
import time
from abc import ABC, abstractmethod
from typing import Union

from aiocsv import AsyncDictWriter
from aiocsv.protocols import WithAsyncWrite


class Collector(ABC):
    """
    Define basic collector interface.
    All child collectors should follow it (csv-like, stdout-like, db-like, etc.)
    """

    fields = [
        "client_id",
        "client_ip",
        "client_port",
        "listen_host",
        "listen_port",
        "data_hex",
        "data_decode",
        "timestamp",
    ]

    def __init__(self, name: str):
        """
        Initialize collector with child class name
        :param name: name of the instance used for logging
        """
        self.name = name
        self.log = logging.getLogger(name)

    @staticmethod
    def build_record(
        client_id: str,
        data: bytes,
        listen_host: str,
        listen_port: int,
        timestamp: Union[None, int] = None,
    ) -> dict:
        """
        Build a record entity
        :param client_id: client identifier
        :param data: data
        :param listen_host: listening host
        :param listen_port: listening port
        :param timestamp: timestamp (optional, or current time)
        :return: None
        """
        try:
            data_decode = str(repr(data.decode("unicode_escape", errors="ignore")))
        except:  # noqa, pylint: disable=bare-except
            data_decode = ""

        data_hex = data.hex()
        client_ip, client_port = client_id.split(":")
        timestamp = timestamp if timestamp else int(time.time())

        return {
            "client_id": client_id,
            "client_ip": client_ip,
            "client_port": client_port,
            "listen_host": listen_host,
            "listen_port": listen_port,
            "data_hex": data_hex,
            "data_decode": data_decode,
            "timestamp": timestamp,
        }

    @abstractmethod
    async def prepare(self):
        """Any required preparations for collector should be implemented here"""

    @abstractmethod
    async def add_record(
        self,
        client_id: str,
        data: bytes,
        listen_host: str,
        listen_port: int,
        timestamp: Union[None, int] = None,
    ):
        """Add record functionality should be implemented here"""


class StdoutTypeCollector(Collector):
    """
    Stdout collector
    """

    def __init__(self):
        """
        Init collector
        """
        super().__init__(name=self.__class__.__name__)

        self.log.debug(
            "stdout collector successfully initialized with name '%s'", self.name
        )

    async def prepare(self) -> None:
        """
        Perform required actions before writing
        :return: None
        """

    async def add_record(
        self,
        client_id: str,
        data: bytes,
        listen_host: str,
        listen_port: int,
        timestamp: Union[None, int] = None,
    ) -> None:
        """
        Add entity
        :param client_id: client identifier
        :param data: data
        :param listen_host: listening host
        :param listen_port: listening port
        :param timestamp: timestamp (optional, or current time)
        :return: None
        """
        record = self.build_record(client_id, data, listen_host, listen_port)

        entities: list[str] = []

        for key, value in record.items():
            entities.append(f"{key}: {value}")

        record_str = "[+] record added: " + ", ".join(entities)

        self.log.info(record_str)


class CsvTypeCollector(Collector):
    """
    CSV-like collector
    """

    def __init__(self, file: WithAsyncWrite):
        """
        Init data collector
        :param file: opened file with async write support
        """
        super().__init__(name=self.__class__.__name__)

        self.file = file
        self.writer = AsyncDictWriter(self.file, fieldnames=self.fields)

        self.log.debug(
            "csv collector successfully initialized with name '%s'", self.name
        )

    async def prepare(self) -> None:
        """
        Perform required actions before writing
        :return: None
        """
        await self.writer.writeheader()

    async def add_record(
        self,
        client_id: str,
        data: bytes,
        listen_host: str,
        listen_port: int,
        timestamp: Union[None, int] = None,
    ) -> None:
        """
        Add entity
        :param client_id: client identifier
        :param data: data
        :param listen_host: listening host
        :param listen_port: listening port
        :param timestamp: timestamp (optional, or current time)
        :return: None
        """
        record = self.build_record(client_id, data, listen_host, listen_port)

        try:
            await self.writer.writerow(record)
        except:  # noqa, pylint: disable=bare-except
            pass
        else:
            self.log.debug(
                "record successfully added for client with id '%s'", client_id
            )

        try:
            await self.file.flush()  # type: ignore[attr-defined]
        except:  # noqa, pylint: disable=bare-except
            pass
