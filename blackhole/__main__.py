"""Module allows to run package as is"""
import asyncio

from blackhole import serve_to_stdout

DEFAULT_HOST = "127.0.0.1"

# Top-20 most scanned Nmap ports
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

DEFAULT_CSV_NAME = "log.csv"

if __name__ == "__main__":
    # pylint: disable=invalid-name
    # main_coroutine = serve_to_csv(DEFAULT_HOST, DEFAULT_PORTS, DEFAULT_CSV_NAME)
    main_coroutine = serve_to_stdout(DEFAULT_HOST, DEFAULT_PORTS)
    asyncio.run(main_coroutine)
