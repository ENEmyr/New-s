import configparser
from sys import path as root_path
from os import path

CONFIG = configparser.ConfigParser()
CURRENT_PATH = path.join(root_path[0], 'configs')

class NewsConfig:
    CONFIG.read_file(open(path.join(CURRENT_PATH, 'config.cfg')))
    Token = CONFIG.get(section='DEFAULT', option='Token')
    APIUrl = CONFIG.get(section='DEFAULT', option='APIUrl')
    RawNewsServices = CONFIG.get(section='DEFAULT', option='RawNewsServices')
    SummarizedNewsServices = CONFIG.get(section='DEFAULT', option='SummarizedNewsServices')
    TokenServices = CONFIG.get(section='DEFAULT', option='TokenServices')

    @staticmethod
    def __setattr__(name, value):
        ''' Overridden __setattr__ method to update configuration file when new attribute got updated.'''
        if name in NewsConfig.__dict__.keys():
            CONFIG.set(section='DEFAULT', option=name, value=value)
            with open(path.join(CURRENT_PATH, 'config.cfg'), 'w') as configfile:
                CONFIG.write(configfile)
            NewsConfig.Token = CONFIG.get(section='DEFAULT', option='Token')
            NewsConfig.APIUrl = CONFIG.get(section='DEFAULT', option='APIUrl')
            NewsConfig.RawNewsServices = CONFIG.get(section='DEFAULT', option='RawNewsServices')
            NewsConfig.SummarizedNewsServices = CONFIG.get(section='DEFAULT', option='SummarizedNewsServices')
            NewsConfig.TokenServices = CONFIG.get(section='DEFAULT', option='TokenServices')
        else:
            raise Exception('Has no attribute.')