#!/usr/bin/env python3

import os
import sys
import yaml
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

if not os.environ.get('XDG_CONFIG_HOME'):
    conf_dir = '~/.config/decant'
else:
    conf_dir = '{}/decant'.format(os.environ['XDG_CONFIG_HOME'])

parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
parser.add_argument('app', nargs='?', help='name of app to run')
parser.add_argument('-c', '--config', default='{}/config.yml'.format(conf_dir),
                    help='config file location')
parser.add_argument('-l', '--log-dir', default='{}/log'.format(conf_dir),
                    help='log directory location')
parser.add_argument('-n', '--native-cmd', default='wine',
                    help='native command to run in the chosen prefix')
parser.add_argument('-w', '--wine-cmd',
                    help='wine command to run in the chosen prefix')
parser.add_argument('-s', '--show-cmd', action='store_true',
                    help='show constructed wine command')
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


log_dir = os.path.expanduser(args.log_dir)

if not os.path.exists(log_dir):
    os.makedirs(log_dir)

config = os.path.expanduser(args.config)

if not os.path.exists(config):
    sys.stderr.write('config file not found: {}\n'.format(config))
    sys.exit(1)

if not args.app:
    for app in read_user_config(config):
        sys.stderr.write('{}\n'.format(app))
    sys.exit(0)

app_config = read_user_config(config, app=args.app)

if not app_config:
    sys.stderr.write('app not found "{}"\n'.format(args.app))
    sys.exit(1)

wine_env = 'WINEPREFIX={}'.format(app_config['wine_prefix'])

if 'wine_env' in app_config:
    wine_env += ' {}'.format(app_config['wine_env'])

if args.wine_cmd:
    wine_cmd = '{}'.format(args.wine_cmd)
else:
    wine_cmd = '{}'.format(app_config['wine_cmd'])

wine_cmd = os.path.expanduser(wine_cmd)

if not os.path.exists(wine_cmd):
    sys.stderr.write('wine command not found: {}'.format(wine_cmd))
    sys.exit(1)

wine_cmd = '"{}"'.format(wine_cmd)

if 'wine_cmd_args' in app_config:
    wine_cmd += ' {}'.format(app_config['wine_cmd_args'])

log = '{}/{}.log'.format(log_dir, args.app)

cmd = '{} {} {} > {} 2>&1'.format(wine_env, args.native_cmd, wine_cmd, log)

if args.show_cmd:
    sys.stderr.write('executing command: {}\n'.format(cmd))

os.system(cmd)
