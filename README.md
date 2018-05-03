# Hetzner-cloud-api

Basic usage examples for [Hetzner Cloud API](https://docs.hetzner.cloud/#top)
Requires an API token exported to as environment variable:

```bash
export API_TOKEN=someverylongstring
```

You can generate a token in the Hetzner web gui under "Access -> API Tokens"

This is really unfinished, especially with regards to error handling and informative output. If you want a more complete solution [hetznercloud-py](https://github.com/elsyms/hetznercloud-py) looks promising.

It consists of an api and a cli tool (hcloudctrl.py).

Personal preferences can be stored in a config file, per default to be found at ```$HOME/.hcloud/config.json``` or supply one with the -f switch.

Requires the excellent [requests](https://github.com/requests/requests) module.
