#!/usr/bin/env python3

import api
import sys

import argparse
parser = argparse.ArgumentParser()


subparsers = parser.add_subparsers(title = "Subcommands", help = "Subcommands", dest = "subcommand")
server_parser = subparsers.add_parser("servers", help = "Server commands")
key_parser = subparsers.add_parser("keys", help = "Ssh key commands")

server_parser.add_argument("-l", "--list", help = "list", action = "store_true")
server_parser.add_argument("-c", "--create", help = "create", action = "store_true")
server_parser.add_argument("-n", "--name", help = "name of item")
server_parser.add_argument("-D", "--delete", help = "delete", action = "store_true")
server_parser.add_argument("-d", "--debug", help = "debug mode", action = "store_true", default = False)

key_parser.add_argument("-l", "--list", help = "list", action = "store_true")
key_parser.add_argument("-c", "--create", help = "create", action = "store_true")
key_parser.add_argument("-n", "--name", help = "name of item")
key_parser.add_argument("-D", "--delete", help = "delete", action = "store_true")
key_parser.add_argument("-d", "--debug", help = "debug mode", action = "store_true", default = False)




args = parser.parse_args()



if __name__ == "__main__":
    h = api.HetznerCloudConnection(debug = args.debug)
    if args.subcommand == "servers":
        if args.list:
            h.debugprint(h.servers)
            for s in h.servers:
                print("- Server {0} - {1} - {2}".format(s['id'], s['name'], s['public_net']['ipv4']['ip']))
        # if args.listkeys:
        #     for k in h.sshkeys:
        #         print("- Ssh key {0} ({1}".format(k['name'], k['fingerprint']))
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
        
