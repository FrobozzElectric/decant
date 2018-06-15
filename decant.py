#!/usr/bin/env python3

import os
import sys
import yaml
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument('app', nargs='?', help='name of app to run')
parser.add_argument('-c', '--config', default='~/.decant/config.yml',
                    help='config file location')
parser.add_argument('-n', '--native-command', default=None,
                    help='native command to run in the chosen prefix')
parser.add_argument('-w', '--wine-command',
                    help='wine command to run in the chosen prefix')
args = parser.parse_args()


def read_user_config(user_config, app=None):
    with open(user_config, 'r') as config:
        try:
            data = yaml.load(config)
            if app:
                return data.get(app)
            else:
                return data
        except yaml.YAMLError as error:
            sys.stderr.write(str(error))
            sys.exit(1)


config = os.path.expanduser(args.config)

if not args.app:
    for item in read_user_config(config):
        sys.stderr.write('{}\n'.format(item))
    sys.exit(0)

app_config = read_user_config(config, app=args.app)

if not app_config:
    sys.stderr.write('app not found "{}"\n'.format(args.app))
    sys.exit(1)

wine_env = 'WINEPREFIX={}'.format(app_config['wine_prefix'])

if 'wine_env' in app_config:
    wine_env += ' {}'.format(app_config['wine_env'])

if args.native_command:
    native_command = args.native_command
else:
    native_command = 'wine'

if args.wine_command:
    wine_command = '"{}"'.format(args.wine_command)
else:
    wine_command = '"{}"'.format(app_config['wine_command'])

if 'wine_command_args' in app_config:
    wine_command += ' {}'.format(app_config['wine_command_args'])

os.system('{} {} {}'.format(wine_env, native_command, wine_command))
