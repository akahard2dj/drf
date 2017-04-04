from configparser import ConfigParser
import os

# FIXME: modify to read file only once

PROPERTY_MODE = 'production'
FILE_PATH = os.path.dirname(os.path.abspath(__file__)) + '/properties/properties-' + PROPERTY_MODE + '.ini'
config = ConfigParser()
config.read(FILE_PATH)


def get(section, name):
    return config.get(section, name)


def get_db(name):
    return get('DATABASE', name)


def get(name):
    return get('DEFAULT', name)


def get_secret(name):
    return get('SECRET', name)
