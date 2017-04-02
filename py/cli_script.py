#!/usr/bin/env python
#-*-coding:utf8;-*-
from __future__ import (
    print_function,
    absolute_import,
    division,
    unicode_literals,
    generators,
    nested_scopes,
)

import json
import logging
import os
import sys

try:
    import argparse
except ImportError:
    print('Install argparse: pip install argparse')
    sys.exit()

from logging import config as log_conf


global args
global config
global log


def __load_args():
    parser = argparse.ArgumentParser()
    parser.description = (
        'Your script\'s long description go here'
    )
    parser.add_argument(
        '--config',
        help=(
            'Specify config file. Must contain a valid JSON format. '
            'This will override the CLI args.'
        )
    )
    parser.add_argument(
        '-L',
        '--loglevel',
        default='INFO',
        help='Set log level (i.e. DEBUG, INFO, WARN, ERROR, CRITICAL)'
    )
    parser.add_argument(
        '--logfile',
        help='Specify log file.'
    )
    return parser.parse_args()


def __load_config(args):
    class Config:
        def __init__(self, logfile=None):
            self.__config = {}
            self.DEBUG = False
            self.SCRIPTNAME = os.path.splitext(os.path.basename(__file__))[0]
            self.SCRIPTDIR = os.path.dirname(os.path.abspath(__file__))
            self.LOGFILE = args.logfile or os.path.join(
                self.SCRIPTDIR,
                '{}.log'.format(self.SCRIPTNAME)
            )
            self.LOGLEVEL = args.loglevel or 'INFO'
            self.__LOGGING = {
                'version': 1,
                'disable_existing_loggers': False,
                'formatters': {
                    'verbose': {
                        'format': (
                            '[%(asctime)s] %(levelname)s %(name)s '
                            '%(pathname)s %(lineno)d - %(message)s'
                        )
                    },
                    'simple': {
                        'format': (
                            '[%(asctime)s] %(levelname)s %(module)s - '
                            '%(message)s'
                        )
                    },
                },
                'handlers': {
                    'file': {
                        'level': 'DEBUG' if self.DEBUG else 'INFO',
                        'class': 'logging.handlers.RotatingFileHandler',
                        'filename': self.LOGFILE,
                        'maxBytes': 1024 * 1024 * 10,  # 10 megabytes
                        'backupCount': 10,
                        'formatter': 'verbose'
                    },
                    'console': {
                        'level': 'DEBUG' if self.DEBUG else 'INFO',
                        'class': 'logging.StreamHandler',
                        'formatter': 'simple'
                    },
                },
                'loggers': {
                    'default': {
                        'handlers': ['file', 'console'],
                        'level': 'DEBUG' if self.DEBUG else 'INFO',
                        'propagate': False,
                    },
                },
            }

            if logfile:
                with open(logfile, 'r') as fh:
                    try:
                        self.__config = json.loads(fh.read())
                        for k, v in self.__config.items():
                            setattr(self, k.upper(), v)
                    except Exception as err:
                        raise err
                    finally:
                        fh.close()

        @property
        def LOGGING(self):
            self.__LOGGING['handlers']['file']['level'] = (
                'DEBUG' if self.DEBUG else self.LOGLEVEL
            )
            self.__LOGGING['handlers']['file']['filename'] = self.LOGFILE
            self.__LOGGING['handlers']['console']['level'] = (
                'DEBUG' if self.DEBUG else self.LOGLEVEL
            )
            self.__LOGGING['loggers']['default']['level'] = (
                'DEBUG' if self.DEBUG else self.LOGLEVEL
            )
            return self.__LOGGING

        @LOGGING.setter
        def LOGGING(self, val):
            self.__LOGGING = val

        @LOGGING.deleter
        def LOGGING(self):
            del self.__LOGGING

        def show(self):
            """Returns config from file"""
            return self.__config

    config = Config(args.config)
    return config


def __init_logger(config):
    if not os.path.exists(config.LOGFILE):
        try:
            with open(config.LOGFILE, 'w') as fh: fh.close()
        except Exception as err:
            raise err
    log_conf.dictConfig(config.LOGGING)
    log = logging.getLogger('default')
    return log


def main():
    global args
    global config
    global log
    log.info('Main code has started')


if __name__ == '__main__':
    global args
    global config
    global log
    args = __load_args()
    config = __load_config(args)
    log = __init_logger(config)
    log.debug('Console args: {}'.format(args))
    if args.config:
        log.debug('Config file: {}'.format(config.show()))
    main()
