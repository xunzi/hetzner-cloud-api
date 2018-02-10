#!/usr/bin/env python3

import api
import sys

import argparse
parser = argparse.ArgumentParser()

parser.add_argument("-l", "--list", help = "list servers", action = "store_true")
parser.add_argument("-k", "--listkeys", help = "list ssh keys", action = "store_true")
parser.add_argument("-d", "--debug", help = "debug mode", action = "store_true", default = False)
parser.add_argument("-c", "--create", help = "create server", action = "store_true")
parser.add_argument("-n", "--name", help = "name of server to create")
parser.add_argument("-D", "--delete", help = "delete a server", action = "store_true")

args = parser.parse_args()

if __name__ == "__main__":
    h = api.HetznerCloudConnection(debug = args.debug)
    if args.list:
        for s in h.servers:
            print("- Server {0} ({1})".format(s['name'], s['public_net']['ipv4']['ip']))
    if args.listkeys:
        for k in h.sshkeys:
            print("- Ssh key {0} ({1}".format(k['name'], k['fingerprint']))
    if args.create:
        if not args.name:
            sys.stderr.write("Please supply a hostname\n")
            sys.exit(1)
        h.create_server(args.name)
        
    if args.delete:
        if not args.name:
            sys.stderr.write("Please supply a hostname\n")
            sys.exit(1)
        _id = h.get_serverid(args.name)
        h.debugprint("{0} - {1}".format(args.name, _id))
        h.delete(_id)
        
