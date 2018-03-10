#!/usr/bin/env python3

import api
import sys

import argparse


parser = argparse.ArgumentParser()


subparsers = parser.add_subparsers(title = "Subcommands", help = "Subcommands", dest = "subcommand")
server_parser = subparsers.add_parser("servers", help = "Server commands")
key_parser = subparsers.add_parser("keys", help = "Ssh key commands")
images_parser = subparsers.add_parser("images", help = "image commands")

server_parser.add_argument("-l", "--list", help = "list", action = "store_true")
server_parser.add_argument("-c", "--create", help = "create", action = "store_true")
server_parser.add_argument("-n", "--name", help = "name of item")
server_parser.add_argument("-D", "--delete", help = "delete", action = "store_true")
server_parser.add_argument("-d", "--debug", help = "debug mode", action = "store_true", default = False)
server_parser.add_argument("-L", "--list-types", help = "list available server types", action = "store_true", dest = "list_types")
server_parser.add_argument("-r", "--reboot", help="soft reboot a server", action = "store_true")
server_parser.add_argument("-t", "--type", help = "image type, run {0} images -l to list available types".format(sys.argv[0]), dest = "imagetype")

key_parser.add_argument("-l", "--list", help = "list", action = "store_true")
key_parser.add_argument("-i", "--import", help = "import key from file", action = "store_true", dest = "importkey")
key_parser.add_argument("-n", "--name", help = "name of item")
key_parser.add_argument("-D", "--delete", help = "delete", action = "store_true")
key_parser.add_argument("-f", "--file", help = "path to public key file to import", dest = "keyfile")
key_parser.add_argument("-d", "--debug", help = "debug mode", action = "store_true", default = False)


images_parser.add_argument("-l", "--list", help = "list", action = "store_true", default = True)



args = parser.parse_args()



if __name__ == "__main__":
    h = api.HetznerCloudConnection()
    if args.subcommand == "servers":
        if args.list:
            h.debugprint(h.servers)
            for s in h.servers:
                print("- Server id {0} - {1} - {2} - {4} ({3})".format(s['id'], s['name'], s['public_net']['ipv4']['ip'], s['status'], s['image']['name']))
        if args.debug:
            h.debug = True

        if args.create:
            if not args.name:
                sys.stderr.write("Please supply a hostname\n")
                sys.exit(1)
            if args.imagetype:
                h.defaults["image"] = args.imagetype
            _resp = h.create_server(args.name)
            h.check_apiresponse(_resp)

        
        if args.delete:
            if not args.name:
                sys.stderr.write("Please supply a hostname\n")
                sys.exit(1)
            _id = h.get_serverid(args.name)
            h.debugprint("{0} - {1}".format(args.name, _id))
            h.delete_server(_id)

        if args.list_types:
            _resp = h.get("server_types")
            for _t in _resp:
                _prices = {}
                for _location in _t['prices']:
                    _prices.update({_location['location']:  round(float(_location['price_monthly']['gross']), 2)})
                print("- {0} - {1} cores - {2} gb ram - {3} gb diskspace ({4} Euro per month".format(_t['name'], _t['cores'], _t['memory'], _t['disk'], _prices) )
            sys.exit(0)

        if args.reboot:
            if not args.name:
               sys.stderr.write("Please supply a hostname\n")
               sys.exit(1)
            _id = h.get_serverid(args.name)
            h.debugprint("found id {0} for server {1}".format(_id, args.name))
            _resp = h.post("servers/{0}/actions/reboot".format(_id))
            if _resp.ok:
                h.debugprint("Reboot action {0} intiated".format(_resp.json()['action']['id']))
            else:
                print("Something went wrong: {0}".format(_resp.json()['error']['message']))
                sys.exit(1)
            sys.exit(0)

    if args.subcommand == "keys":
        if args.list:
            for k in h.sshkeys:
                print("- Ssh key id {0} - {1} - {2}".format(k['id'], k['name'], k['fingerprint']))
        if args.importkey:
            if not args.name:
                sys.stderr.write("Please supply a key name\n")
                sys.exit(1)
            with open(args.keyfile) as keyfile:
                keystring =  keyfile.read()
                _resp = h.create_key(name=args.name, key = keystring)
                h.debugprint(_resp)
                if _resp.ok:
                    print("Key {0} created".format(args.name))
                else:
                    sys.stderr.write("Error creating key: {0}".format(_resp.json()['error']['message']))
                    sys.exit(1)
        if args.delete:
            if not args.name:
                sys.stderr.write("Please supply a key name\n")
                sys.exit(1)
            _keyid = h.get_keyid(args.name)
            h.debugprint("Found key {0}".format(_keyid))
            h.delete_key(_keyid)
            sys.exit(0)

    if args.subcommand == "images":
        if args.list:
            _resp = h.get("images")
            for _i in _resp:
                print("- {0} - {1} - type {2}".format(_i['id'], _i['name'], _i['type']))
