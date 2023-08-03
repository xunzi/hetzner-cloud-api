#!/usr/bin/env python3

import api
import sys
import os
import os.path
import json
import argparse


parser = argparse.ArgumentParser()
parser.add_argument("-c", "--configfile", help="path to configfile, default $HOME/.hcloud/config.json",
                    default="{home}/.hcloud/config.json".format(home=os.environ['HOME']))
parser.add_argument("-d", "--debug", help="debug mode",
                    action="store_true", default=False)

subparsers = parser.add_subparsers(title="Subcommands", help="Subcommands", dest="subcommand")
server_parser = subparsers.add_parser("servers", help="Server commands")
key_parser = subparsers.add_parser("keys", help="Ssh key commands")
images_parser = subparsers.add_parser("images", help="image commands")
servertype_parser = subparsers.add_parser("servertypes", help="servertype commands")
floatip_parser = subparsers.add_parser("floatingips", help="floating ip commands")
location_parser = subparsers.add_parser("locations", help="location commands")
volume_parser = subparsers.add_parser("volumes", help="volume commands")

server_parser.add_argument("-l", "--list", help="list", action="store_true")
server_parser.add_argument("-j", "--json", help="Json output suitable as nasible inventory", default=False, action="store_true")
server_parser.add_argument("-c", "--create", help="create", action="store_true")
server_parser.add_argument("-n", "--name", help="name of item")
server_parser.add_argument("-D", "--delete", help="delete", action="store_true")
server_parser.add_argument("-i", "--image", help="image type, run {0} images -l to list available types".format(sys.argv[0]), dest="imagetype")
server_parser.add_argument("-t", "--type", help="server type", dest="servertype", default=api.HetznerCloudConnection().defaults["server_type"])
server_parser.add_argument("-k", "--key", help="ssh key to install", dest="key", default="")
server_parser.add_argument("-a", "--action", choices=['shutdown', 'reboot', 'reset', 'poweron', 'poweroff', 'reset_password'])
server_parser.add_argument("-p", "--protect", help="toggle server protection", choices=["both", "none"])
server_parser.add_argument("-R", "--rebuild", help="Rebuild Server, if no type arg is given will re-use image type", dest="rebuild", action="store_true")
server_parser.add_argument("-L", "--location", help="Location", default="fsn1", dest="location")

key_parser.add_argument("-l", "--list", help="list", action="store_true")
key_parser.add_argument("-i", "--import", help="import key from file", action="store_true", dest="importkey")
key_parser.add_argument("-n", "--name", help="name of item")
key_parser.add_argument("-D", "--delete", help="delete", action="store_true")
key_parser.add_argument("-f", "--file", help="path to public key file to import", dest="keyfile")

images_parser.add_argument("-l", "--list", help="list", action="store_true", default=True)

servertype_parser.add_argument("-l", "--list", help="list available server types", action="store_true")

floatip_parser.add_argument('-l', '--list', help="list available floating ips", action="store_true")

location_parser.add_argument('-l', "--list", help="list locations", action="store_true")

volume_parser.add_argument("-l", "--list", help="List volumes", action="store_true")
volume_parser.add_argument("-c", "--create", help="Create volume", action="store_true")
volume_parser.add_argument("-D", "--delete", help="Delete volume", action="store_true")
volume_parser.add_argument("-n", "--name", help="Name for the new volume")
volume_parser.add_argument("-S", "--server", help="Server to attach volume to")
volume_parser.add_argument("-s", "--size", help="Size of volume in GB, defaults to 10 GB", default=10)
volume_parser.add_argument("-a", "--automount", help="automatically mount volume", action="store_true")
volume_parser.add_argument("-f", "--format", help="format volume", choices=['ext4', 'xfs'])

args = parser.parse_args()

if __name__ == "__main__":
    h = api.HetznerCloudConnection()
    if args.debug:
        h.debug = True
    if os.path.exists("{home}/.hcloud".format(home=os.environ['HOME'])):
        if os.path.exists(args.configfile):
            try:
                h.defaults.update(json.load(open(args.configfile)))
                h.debugprint("loaded preferences from config file {configfile}".format(configfile=args.configfile))
            except IOError:
                h.debugprint("Could not load config file {configfile}".format(configfile=args.configfile))
                h.debugprint(sys.exc_info()[0])
        else:
            json.dump(h.defaults, open(args.configfile, 'w'), indent=2, skipkeys=True)
            h.debugprint("Created config file {configfile}".format(configfile=args.configfile))
    else:
        os.mkdir("{home}/.hcloud".format(home=os.environ['HOME']))
        json.dump(h.defaults, open(args.configfile, 'w'), indent=2)
        h.debugprint("Created config file {configfile}".format(configfile=args.configfile))

    if args.subcommand == "servers":
        if args.list:
            for s in h.servers:
                if len(h.floatingips) == 0:
                    floatip_info = ''
                for floatip in h.floatingips:
                    if floatip['server'] == s['id']:
                        floatip_info = "Floating Ip {f_ip}@{location}.".format(f_ip=floatip['ip'], location=floatip['home_location']['name'])
                    else:
                        floatip_info = ''
                if args.json:
                    inventory = {"hostvars": {s['name']: {'ansible_host': s['public_net']['ipv4']['ip']}}}
                    print(json.dumps(inventory))
                else:
                    print("- Server id {id} - {name} - {ipv4}/{ipv6} - {datacenter} {image}/{servertype} ({state}) [Protected against Deletion: {deletion}, Rebuild: {rebuild}] {floatingip}".format(
                        id=s['id'],
                        name=s['name'],
                        ipv4=s['public_net']['ipv4']['ip'],
                        ipv6=s['public_net']['ipv6']['ip'],
                        state=s['status'],
                        image=s['image']['name'],
                        servertype=s["server_type"]['name'],
                        deletion=s["protection"]["delete"],
                        rebuild=s["protection"]["rebuild"],
                        datacenter=s["datacenter"]["name"],
                        floatingip=floatip_info
                        )
                    )

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
                h.defaults["ssh_keys"] = [_k]
            if args.location:
                h.defaults["location"] = args.location
            _resp = h.create_server(args.name)
            if not h.defaults["ssh_keys"]:
                print("root-PW: {rootpw}".format(rootpw=_resp.json()["root_password"]))
            h.check_apiresponse(_resp, "server {name} created".format(name=args.name))

        if args.delete:
            if not args.name:
                sys.stderr.write("Please supply a hostname\n")
                sys.exit(1)
            _id = h.get_serverid(args.name)
            h.debugprint("{name} - {id}".format(name=args.name, id=_id))
            _resp = h.delete_server(_id)
            h.check_apiresponse(_resp, "server {name} deleted".format(name=args.name))

        if args.action:
            if not args.name:
                sys.stderr.write("Please supply a hostname\n")
                sys.exit(1)
            _id = h.get_serverid(args.name)
            h.debugprint("found id {id} for server {name}".format(id=_id, name=args.name))
            _resp = h.post("servers/{id}/actions/{action}".format(id=_id, action=args.action))
            if args.action == 'reset_password':
                print("New root password for Server {server}: {password}".format(server=args.name, password=_resp.json()['root_password']))
            h.check_apiresponse(_resp)
        # protection is currently only possible for both deletion and rebuild or none of the two
        # TODO add logic to handle both cases separately
        if args.protect:
            if not args.name:
                sys.stderr.write("Please supply a hostname\n")
                sys.exit(1)
            _id = h.get_serverid(args.name)
            if args.protect == "both":
                _resp = h.post("servers/{id}/actions/change_protection".format(id=_id), payload={"delete": True, "rebuild": True})
                h.check_apiresponse(_resp)
            elif args.protect == "none":
                _resp = h.post("servers/{id}/actions/change_protection".format(id=_id), payload={"delete": False, "rebuild": False})
                h.check_apiresponse(_resp)

        if args.rebuild:
            if not args.name:
                sys.stderr.write("Please supply a hostname\n")
                sys.exit(1)
            _s = h.get_server(servername=args.name)
            if not args.imagetype:
                image = _s['image']['name']
            else:
                image = args.imagetype
            _id = _s['id']
            _resp = h.post("servers/{id}/actions/rebuild".format(id=_id), payload={'image': image})
            h.check_apiresponse(_resp)

    if args.subcommand == "keys":
        if args.list:
            for k in h.sshkeys:
                print("- Ssh key id {id} - {name} - {fingerprint}".format(id=k['id'], name=k['name'], fingerprint=k['fingerprint']))
            sys.exit(0)
        if args.importkey:
            if not args.name:
                sys.stderr.write("Please supply a key name\n")
                sys.exit(1)
            with open(args.keyfile) as keyfile:
                keystring = keyfile.read()
                _resp = h.create_key(name=args.name, key=keystring)
                h.check_apiresponse(_resp, "Ssh key {name} created".format(name=args.name))
        if args.delete:
            if not args.name:
                sys.stderr.write("Please supply a key name\n")
                sys.exit(1)
            _keyid = h.get_keyid(args.name)
            h.debugprint("Found key {id}".format(id=_keyid))
            _resp = h.delete_key(_keyid)
            h.check_apiresponse(_resp, "Key {name} deleted".format(name=args.name))

    if args.subcommand == "images":
        if args.list:
            _resp = h.get("images")
            for _i in _resp:
                print("- {id} - {name} - type {imagetype}".format(id=_i['id'], name=_i['name'], imagetype=_i['type']))

    if args.subcommand == "servertypes":
        if args.list:
            _resp = h.get("server_types")
            for _t in _resp:
                print("- {id} - {name} - {arch} - {cores} cores, {memory} GB RAM, {disk} GB disk size, {storage} storage".format(
                    id=_t['id'],
                    name=_t['name'],
                    arch = _t['architecture'],
                    cores=_t['cores'],
                    memory=_t['memory'],
                    disk=_t['disk'],
                    storage=_t['storage_type']))
        sys.exit(0)

    if args.subcommand == "floatingips":
        if args.list:
            for _i in h.floatingips:
                print("- {id} - {ip} - {description} - {server} - {location}".format(
                    id=_i['id'],
                    ip=_i['ip'],
                    description=_i['description'],
                    server=h.get_server_by_id(_i['server']),
                    location=_i['home_location']['name']))


    if args.subcommand == "locations":
        if args.list:
            _resp = h.get('locations')
            for _l in _resp:
                print("{id} - {name} - {description} - {city} - {country}".format(
                    id=_l['id'],
                    name=_l["name"],
                    description=_l['description'],
                    city=_l['city'],
                    country=_l['country'])
                )
    if args.subcommand == "volumes":
        if args.list:
            _resp = h.get("volumes")
            for _v in _resp:
                if _v['server']:
                    server_name = h.get_server(servername=_v['server'])
                    print("{id} - {name} - {size} GB - attached to server {server_name}".format(
                        id=_v['id'],
                        name=_v['id'],
                        size=_v['size'],
                        server_name=h.get_server(serverid=_v['server'])['name'])
                    )
                else:
                    print("{id} - {name} - {size} GB - curently not attached".format(
                        id=_v['id'],
                        name=_v['name'],
                        size=_v['size'])
                    )
        if args.create:
            if not args.name:
                sys.stderr.write("Please supply a hostname\n")
                sys.exit(1)
            vol_spec = {'name': args.name, 'size': args.size}
            if args.server:
                vol_spec['server'] = h.get_serverid(args.server)
            if args.automount:
                vol_spec['automount'] = args.automount
            if args.format:
                vol_spec['format'] = args.format
            _resp = h.post("volumes", payload=vol_spec)
            h.check_apiresponse(_resp, "Volume {volname} created".format(volname=args.name))
        if args.delete:
            if not args.name:
                sys.stderr.write("Please supply a hostname\n")
                sys.exit(1)
            for v in h.volumes:
                if v['name'] == args.name:
                    v_id = v['id']
            _resp = h.delete("volumes/{id}".format(id=v_id))
            h.check_apiresponse(_resp, "Volume {v_id} deleted".format(v_id=v_id))
