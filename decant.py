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
parser.add_argument('-n', '--native-cmd',
                    help='run native command in the chosen prefix and exit')
parser.add_argument('-w', '--wine-cmd',
                    help='wine command to run in the chosen prefix')
parser.add_argument('-wa', '--wine-cmd-arg',
                    help='arg(s) for the above wine command')
parser.add_argument('-s', '--show-cmd', action='store_true',
                    help='show constructed wine command')
args = parser.parse_args()


class Runner:

    def __init__(self, app_config):
        self.config = app_config
        self.wine_env = 'WINEPREFIX={}'.format(app_config['wine_prefix'])
        self.wine = app_config.get('wine', 'wine')
        self.pre_cmds = app_config.get('pre_cmd', [])
        self.wine_cmd = app_config.get('wine_cmd', '')
        self.post_cmds = app_config.get('post_cmd', [])
        self.log = None

    def construct_wine_env(self):
        for env in self.config.get('wine_env', []):
            self.wine_env += ' {}'.format(env)

    def construct_wine_cmd(self, wine_cmd):
        cmd_base = '{} {} {} > {} 2>&1'
        if wine_cmd:
            cmd = os.path.expanduser(wine_cmd)
        else:
            cmd = os.path.expanduser(self.wine_cmd)
        if not os.path.exists(cmd):
            sys.stderr.write('wine command not found: {}'.format(cmd))
            sys.exit(1)
        if args.wine_cmd_arg:
            cmd = '"{}" {}'.format(cmd, args.wine_cmd_arg)
        elif 'wine_cmd_arg' in self.config and not args.wine_cmd:
            cmd = '"{}" {}'.format(cmd, self.config['wine_cmd_arg'])
        else:
            cmd = '"{}"'.format(cmd)
        cmd = cmd_base.format(self.wine_env, self.wine, cmd, self.log)
        self.wine_cmd = cmd

    def exec_pre_cmds(self):
        for cmd in self.pre_cmds:
            if args.show_cmd:
                sys.stderr.write('executing pre cmd: {}\n'.format(cmd))
            os.system(cmd)

    def exec_wine_cmd(self, wine_cmd=None):
        self.construct_wine_env()
        self.construct_wine_cmd(wine_cmd)
        if args.show_cmd:
            sys.stderr.write('executing wine cmd: {}\n'.format(self.wine_cmd))
        try:
            os.system(self.wine_cmd)
        except KeyboardInterrupt:
            os.system('pkill -f .exe')

    def exec_post_cmds(self):
        for cmd in self.post_cmds:
            if args.show_cmd:
                sys.stderr.write('executing post cmd: {}\n'.format(cmd))
            os.system(cmd)

    def exec_native_cmd(self, cmd):
        self.construct_wine_env()
        cmd = '{} {}'.format(self.wine_env, cmd)
        if args.show_cmd:
            sys.stderr.write('executing native cmd: {}\n'.format(cmd))
        os.system(cmd)


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

if not os.path.exists(config):
    sys.stderr.write('config file not found: {}\n'.format(config))
    sys.exit(1)

if not args.app:
    for app in read_user_config(config):
        sys.stderr.write('{}\n'.format(app))
    sys.exit(0)

app_config = read_user_config(config, app=args.app)

if not app_config:
    sys.stderr.write('app not found: {}\n'.format(args.app))
    sys.exit(1)

runner = Runner(app_config)

if args.native_cmd:
    runner.exec_native_cmd(args.native_cmd)
    sys.exit(0)

log_dir = os.path.expanduser(args.log_dir)

if not os.path.exists(log_dir):
    os.makedirs(log_dir)

runner.log = '{}/{}.log'.format(log_dir, args.app)

if args.wine_cmd:
    runner.exec_wine_cmd(args.wine_cmd)
    sys.exit(0)

runner.exec_pre_cmds()
runner.exec_wine_cmd()
runner.exec_post_cmds()
