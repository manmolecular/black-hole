"""Module allows to run package as is"""
# pylint: disable=invalid-name
import asyncio
import logging
import pathlib
import sys

import yaml

from blackhole import serve_to_stdout, serve_to_csv

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
    extra_params = {
        "read_size": listener_conf["read_size"],
        "delay": listener_conf["delay"],
    }

    collector_conf = conf.get("collector", {})
    collector_type = collector_conf["type"].lower()

    match collector_type:
        case "csv":
            csv_params = collector_conf["csv"]
            main_coroutine = serve_to_csv(
                **base_params,
                **csv_params,
                **extra_params,
            )
        case "stdout":
            stdout_params = collector_conf["stdout"]
            if stdout_params is None:
                stdout_params = {}
            main_coroutine = serve_to_stdout(
                **base_params,
                **stdout_params,
                **extra_params,
            )
        case _:
            sys.exit("invalid collector type")

    asyncio.run(main_coroutine)
