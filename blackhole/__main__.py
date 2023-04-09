"""Module allows to run package as is"""
import asyncio

from blackhole import serve

if __name__ == "__main__":
    asyncio.run(serve())
