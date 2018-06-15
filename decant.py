#!/usr/bin/env python3

import os
import sys
import yaml
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument('app', help='name of app to run')
parser.add_argument('-c', '--config', default='~/.decant/config.yml',
                    help='config file location')
parser.add_argument('-n', '--native-command', default=None,
                    help='native command to run in the chosen prefix')
parser.add_argument('-w', '--wine-command',
                    help='wine command to run in the chosen prefix')


args = parser.parse_args()


def read_user_config(user_config, app):
    with open(user_config, 'r') as config:
        try:
            data = yaml.load(config)
            return data.get(app)
        except yaml.YAMLError as error:
            sys.stderr.write(str(error))
            sys.exit(1)


app_config = read_user_config(os.path.expanduser(args.config), args.app)

if not app_config:
    sys.stderr.write('app not found "{}"\n'.format(args.app))
    sys.exit(1)

if args.native_command:
    native_command = args.native_command
else:
    native_command = 'wine'

if args.wine_command:
    wine_command = args.wine_command
else:
    wine_command = app_config['wine_command']

wine_prefix = app_config['wine_prefix']

#wine_command = wine_command.replace(' ', '\ ')
#wine_command = wine_command.replace('(', '\(')
#wine_command = wine_command.replace(')', '\)')
print(wine_command)

command = 'WINEPREFIX={} {} {}'. format(wine_prefix,
                                        native_command,
                                        wine_command)

os.system(command)
