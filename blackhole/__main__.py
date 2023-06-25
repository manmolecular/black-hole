"""Module allows to run package as is"""
# pylint: disable=invalid-name
import asyncio
import logging
import pathlib
import sys

import yaml

from blackhole import Server

CONFIG_NAME = "config.yaml"

# Suppress asyncio logging; allow only 'FATAL' messages
logging.getLogger("asyncio").setLevel(logging.FATAL)


def load_config() -> dict:
    """
    Load the YAML configuration
    :return: YAML configuration as dict
    """
    src_root = pathlib.Path(__file__).parents[1]
    config_path = src_root.joinpath(CONFIG_NAME)

    with open(config_path, mode="r", encoding="utf-8") as config_file:
        config = yaml.safe_load(config_file)

    return config


if __name__ == "__main__":
    conf = load_config()

    logger_conf = conf.get("logger", {})
    logging.basicConfig(level=logger_conf["level"], format=logger_conf["format"])

    listener_conf = conf.get("listener", {})
    base_params = {
        "host": listener_conf["host"],
        "ports": listener_conf["ports"],
    }
    listener_params = {
        "read_size": listener_conf["read_size"],
        "delay": listener_conf["delay"],
    }

    collector_conf = conf.get("collector", {})
    collector_type = collector_conf["type"].lower()

    server = Server(host=base_params["host"], ports=base_params["ports"])

    match collector_type:
        case "csv":
            csv_params = collector_conf["csv"]
            coroutine = server.serve_to_csv(**csv_params, **listener_params)
        case "stdout":
            stdout_params = collector_conf["stdout"]
            if stdout_params is None:
                stdout_params = {}
            coroutine = server.serve_to_stdout(**stdout_params, **listener_params)
        case _:
            sys.exit("invalid collector type")

    try:
        asyncio.run(coroutine)
    except KeyboardInterrupt:
        logging.debug("start graceful shutdown")
        asyncio.run(server.stop())

    logging.debug("graceful shutdown is finished")
