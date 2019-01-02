# Hetzner-cloud-api

Basic usage examples for [Hetzner Cloud API](https://docs.hetzner.cloud/#top)
Requires an API token exported to as environment variable:

```bash
export HCLOUD_TOKEN=someverylongstring
```

You can generate a token in the Hetzner web gui under "Access -> API Tokens"

This is really unfinished, especially with regards to error handling and informative output. If you want a more complete solution [hetznercloud-py](https://github.com/elsyms/hetznercloud-py) looks promising.

Of course the official [cli client written in Golang](https://github.com/hetznercloud/cli) should be mentioned as well.

Personal preferences can be stored in a config file, per default to be found at ```$HOME/.hcloud/config.json``` or supply one with the -f switch.

Requires the excellent [requests](https://github.com/requests/requests) module.

## First Steps

```bash
~/sandkasten/hetznercloud% export API_TOKEN=someverylongstring
~/sandkasten/hetznercloud% ./hcloudctrl.py -h
usage: hcloudctrl.py [-h] [-c CONFIGFILE] [-d]
                     {servers,keys,images,servertypes,floatingips,locations}
                     ...

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIGFILE, --configfile CONFIGFILE
                        path to configfile
  -d, --debug           debug mode

Subcommands:
  {servers,keys,images,servertypes,floatingips,locations}
                        Subcommands
    servers             Server commands
    keys                Ssh key commands
    images              image commands
    servertypes         servertype commands
    floatingips         floating ip commands
    locations           location commands
~/sandkasten/hetznercloud% ./hcloudctrl.py servers -c -n myfirstcloudserver
server myfirstcloudserver created
~/sandkasten/hetznercloud% ./hcloudctrl.py servers -l
- Server id 724668 - myfirstcloudserver - 1.2.3.4/2a01:x:x:xc::/64 - ubuntu-18.04/cx11 (starting)
~/sandkasten/hetznercloud% ./hcloudctrl.py servers -D -n myfirstcloudserver
server myfirstcloudserver deleted
```