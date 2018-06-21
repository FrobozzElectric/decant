# What is decant?
`decant` is a script for configuring your wine apps so they always run with the right `WINEPREFIX`, environment variables and .EXEs. Instead of remembering long incantations to launch a certain game, just configure it once with some YAML and run `decant configured-app-name`.

# Installation
```
$ git clone https://github.com/FrobozzElectric/decant
```
```
$ cd decant
```
```
$ ./install.sh
```

# App config
The config file is located at `$XDG_CONFIG_HOME/decant/config.yml`. This is usually `~/.config/decant/config.yml` in reality. Only the fields `wine_prefix` and `wine_cmd` are required. The fields `pre_cmd`, `post_cmd` and `wine_env` are all lists that can have as many entries as needed.

Here's a real life config example:

```yaml
witcher-3:
  wine_env:
    - 'DXVK_HUD=fps'
  wine_prefix: '~/.wine-dxvk'
  wine_cmd: '~/.wine-dxvk/drive_c/Program Files (x86)/Steam/Steam.exe'
  wine_cmd_arg: '-applaunch 292030'
  notes: 'working with wine-3.10 (Staging)/dxvk-0.54'
```

Running `witcher-3` would look like:

```
$ decant witcher-3
```

If you're not sure what you have configured, run `decant` without any arguments and it will print out all the configured apps it knows about:

```
$ decant
eye
overwatch
overwatch-launcher
stalker-soc
warframe
witcher-3
```

My real configs are kept here for more examples: https://github.com/FrobozzElectric/decant-config

---
Boss makes a dollar, I make a dime, that's why I document personal projects on company time 😇
