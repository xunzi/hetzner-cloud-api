#!/usr/bin/env python3

import api
import sys

import argparse


parser = argparse.ArgumentParser()


subparsers = parser.add_subparsers(title = "Subcommands", help = "Subcommands", dest = "subcommand")
server_parser = subparsers.add_parser("servers", help = "Server commands")
key_parser = subparsers.add_parser("keys", help = "Ssh key commands")
images_parser = subparsers.add_parser("images", help = "image commands")
servertype_parser = subparsers.add_parser("servertypes", help = "servertype commands")

server_parser.add_argument("-l", "--list", help = "list", action = "store_true")
server_parser.add_argument("-c", "--create", help = "create", action = "store_true")
server_parser.add_argument("-n", "--name", help = "name of item")
server_parser.add_argument("-D", "--delete", help = "delete", action = "store_true")
server_parser.add_argument("-d", "--debug", help = "debug mode", action = "store_true", default = False)
server_parser.add_argument("-i", "--image", help = "image type, run {0} images -l to list available types".format(sys.argv[0]), dest = "imagetype")
server_parser.add_argument("-t", "--type", help = "server type", dest = "servertype", default = api.HetznerCloudConnection().defaults["server_type"])
server_parser.add_argument("-k", "--key", help = "ssh key to install", dest = "key", default = "" )
server_parser.add_argument("-a", "--action", choices = ['shutdown', 'reboot', 'reset', 'poweron', 'poweroff', 'reset_password'])

key_parser.add_argument("-l", "--list", help = "list", action = "store_true")
key_parser.add_argument("-i", "--import", help = "import key from file", action = "store_true", dest = "importkey")
key_parser.add_argument("-n", "--name", help = "name of item")
key_parser.add_argument("-D", "--delete", help = "delete", action = "store_true")
key_parser.add_argument("-f", "--file", help = "path to public key file to import", dest = "keyfile")
key_parser.add_argument("-d", "--debug", help = "debug mode", action = "store_true", default = False)


images_parser.add_argument("-l", "--list", help = "list", action = "store_true", default = True)

servertype_parser.add_argument("-l", "--list", help = "list available server types", action = "store_true")



args = parser.parse_args()



if __name__ == "__main__":
    h = api.HetznerCloudConnection()
    if args.subcommand == "servers":
        if args.list:
            h.debugprint(h.servers)
            for s in h.servers:
                print("- Server id {0} - {1} - {2} - {4}/{5} ({3})".format(s['id'], s['name'], s['public_net']['ipv4']['ip'], s['status'], s['image']['name'], s["server_type"]['name']))
        if args.debug:
            h.debug = True

        if args.create:
            if not args.name:
                sys.stderr.write("Please supply a hostname\n")
                sys.exit(1)
            if args.imagetype:
                h.defaults["image"] = args.imagetype
            if args.servertype:
                h.defaults['server_type'] = args.servertype
            if args.key:
                _k = h.get_keyid(args.key)
                h.defaults["ssh_keys"] = [ _k ]
            _resp = h.create_server(args.name)
            h.check_apiresponse(_resp, "server {0} created".format(args.name))

        
        if args.delete:
            if not args.name:
                sys.stderr.write("Please supply a hostname\n")
                sys.exit(1)
            _id = h.get_serverid(args.name)
            h.debugprint("{0} - {1}".format(args.name, _id))
            _resp = h.delete_server(_id)
            h.check_apiresponse(_resp, "server {0} deleted".format(args.name))

        if args.action:
            if not args.name:
               sys.stderr.write("Please supply a hostname\n")
               sys.exit(1)
            _id = h.get_serverid(args.name)
            h.debugprint("found id {0} for server {1}".format(_id, args.name))
            _resp = h.post("servers/{id}/actions/{action}".format(id = _id, action = args.action))
            if args.action == 'reset_password':
                print("New root password for Server {server}: {password}".format(server=args.name, password =_resp.json()['root_password']))
            h.check_apiresponse(_resp)
        

    if args.subcommand == "keys":
        if args.list:
            for k in h.sshkeys:
                print("- Ssh key id {0} - {1} - {2}".format(k['id'], k['name'], k['fingerprint']))
            sys.exit(0)
        if args.importkey:
            if not args.name:
                sys.stderr.write("Please supply a key name\n")
                sys.exit(1)
            with open(args.keyfile) as keyfile:
                keystring =  keyfile.read()
                _resp = h.create_key(name=args.name, key = keystring)
                h.check_apiresponse(_resp, "Ssh key {0} created".format(args.name))
        if args.delete:
            if not args.name:
                sys.stderr.write("Please supply a key name\n")
                sys.exit(1)
            _keyid = h.get_keyid(args.name)
            h.debugprint("Found key {0}".format(_keyid))
            _resp = h.delete_key(_keyid)
            h.check_apiresponse(_resp, "Key {0} deleted".format(args.name))

    if args.subcommand == "images":
        if args.list:
            _resp = h.get("images")
            for _i in _resp:
                print("- {0} - {1} - type {2}".format(_i['id'], _i['name'], _i['type']))

    if args.subcommand == "servertypes":
        if args.list:
            _resp = h.get("server_types")
            for _t in _resp:
                print("- {0} - {1} - {2} cores, {3} GB RAM, {4} GB disk size, {5} storage".format(_t['id'], _t['name'], _t['cores'], _t['memory'], _t['disk'], _t['storage_type']))
            sys.exit(0)
