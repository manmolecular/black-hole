"""Describe a setup procedure"""
from setuptools import setup  # type: ignore[import]

with open("requirements.txt", encoding="utf-8", mode="r") as f:
    requirements = f.read().splitlines()

setup(
    name="black-hole",
    version="",
    packages=["blackhole"],
    url="https://github.com/manmolecular/black-hole",
    license="",
    author="https://github.com/manmolecular",
    description="Collect and log payloads on open ports",
    install_requires=requirements,
)
