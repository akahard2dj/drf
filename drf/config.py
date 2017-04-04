from configparser import ConfigParser

config = ConfigParser()
config.read('/properties/properties-production.txt')


def get_config():
    return config


def test():
    c = get_config()
    v = c.get('DJANGO_SECRET_KEY')
    print(v)

test()