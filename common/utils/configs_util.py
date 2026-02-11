import json
import logging
import os

logger = logging.getLogger(__name__)
curr_dir = os.path.abspath(os.path.dirname(__file__))
config_dir = os.path.abspath(os.path.dirname(os.path.dirname(curr_dir)))


def load_config(env_name='us'):
    env_name = env_name if env_name is not None else "us"
    rel_path = f'common/config/{env_name}.json'
    config = load_file_from_root(rel_path)
    return config


def load_file_from_root(rel_file):
    env_file_path = f'{config_dir}/{rel_file}'
    load_json = json.load(open(env_file_path))
    return load_json


def create_directory_if_necessary(directory):
    if not os.path.exists(directory):
        try:
            logger.info("Creating directory: {}".format(directory))
            os.makedirs(directory)
        except FileExistsError:
            logger.info("Directory already exists")