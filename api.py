#!/usr/bin/env python3

import requests
import sys
import os

APIVERSION = "v1"
APIBASE = "https://api.hetzner.cloud/{apiversion}".format(apiversion=APIVERSION)


class HetznerCloudConnection:
    def __init__(self, debug=False):
        self. debug = debug
        self.session = requests.Session()
        try:
            self.token = os.environ['HCLOUD_TOKEN']
        except KeyError:
            sys.stderr.write("Missing env var HCLOUD_TOKEN\n")
            sys.exit(1)
        self.session.headers = {"Authorization": "Bearer {token}".format(token=self.token)}
        self.servers = []
        self.sshkeys = []
        self.floatingips = []
        self.volumes = []
        self.get_servers()
        self.get_sshkeys()
        self.get_floatingips()
        self.get_volumes()
        self.defaults = {
            'ssh_keys': [],
            'server_type': 'cx11',
            'image': 'ubuntu-18.04',
            'location': 'fsn1'
        }
        if len(self.sshkeys) == 1:
            self.defaults['ssh_keys'].append(self.sshkeys[0]['id'])

    def debugprint(self, msg):
        if self.debug:
            sys.stderr.write("{msg}\n".format(msg=msg))

    def check_apiresponse(self, resp, okmsg=""):
        if not resp.ok:
            sys.stderr.write("An errror occurred: {errormsg}".format(errormsg=resp.json()['error']['message']))
            sys.exit(1)
        else:
            print(okmsg)
            self.debugprint("Status ok")
            sys.exit(0)

    def get(self, path):
        _resp = self.session.get("{apibase}/{path}".format(apibase=APIBASE, path=path))
        # self.debugprint(_resp.text)
        return _resp.json()[path]

    def post(self, path, payload={}):
        self.session.headers.update({"Content-Type": "application/json"})
        _resp = self.session.post("{apibase}/{path}".format(apibase=APIBASE, path=path), json=payload)
        # self.debugprint(_resp.text)
        return _resp

    def delete(self, path, payload={}):
        self.session.headers.update({"Content-Type": "application/json"})
        _resp = self.session.delete("{apibase}/{path}".format(apibase=APIBASE, path=path), json=payload)
        return _resp

    def delete_server(self, server_id):
        self.session.headers.update({"Content-Type": "application/json"})
        _resp = self.session.delete("{apibase}/servers/{id}".format(apibase=APIBASE, id=server_id))
        # self.debugprint(_resp.text)
        return _resp

    def get_servers(self):
        _resp = self.get("servers")
        for _s in _resp:
            self.servers.append(_s)
        # self.debugprint("Found {0} servers".format(len(self.servers)))
        # for _s in self.servers:
        #    self.debugprint("{0} - {1} - {2}".format(_s['id'], _s['name'], _s['public_net']['ipv4']['ip']))

    def get_floatingips(self):
        _resp = self.get("floating_ips")
        for _ip in _resp:
            self.floatingips.append(_ip)

    def get_volumes(self):
        _resp = self.get("volumes")
        for _v in _resp:
            self.volumes.append(_v)

    def get_serverid(self, name):
        _id = None
        for s in self.servers:
            if s['name'] == name:
                _id = s['id']
        return _id

    def get_server_by_id(self, serverid):
        _name = None
        for _s in self.servers:
            if _s['id'] == serverid:
                _name = _s['name']
        return _name

    def get_server(self, serverid="", servername=""):
        if serverid:
            for _s in self.servers:
                if _s['id'] == serverid:
                    return _s
        elif servername:
            for _s in self.servers:
                if _s['name'] == servername:
                    return _s
        else:
            return False

    def get_sshkeys(self):
        _resp = self.get("ssh_keys")
        # self.debugprint(_resp)
        for _key in _resp:
            self.sshkeys.append(_key)
        # self.debugprint("Found {0} keys".format(len(self.sshkeys)))
        # for _key in self.sshkeys:
        #     self.debugprint("Key id {0}, name {1}, fingerprint {2}".format(_key['id'], _key['name'], _key['fingerprint']))

    def create_server(self, name=""):
        server_spec = self.defaults
        if name:
            server_spec['name'] = name
        _resp = self.post("servers", payload=server_spec)
        # self.debugprint(_resp)
        return _resp

    def create_key(self, name="", key=""):
        key_spec = {'name': name, 'public_key': key}
        _resp = self.post("ssh_keys", payload=key_spec)
        return _resp

    def get_keyid(self, name=""):
        _id = None
        for k in self.sshkeys:
            if k['name'] == name:
                _id = k['id']
        return _id

    def delete_key(self, keyid):
        # self.session.headers.update({"Content-Type": "application/json"})
        _resp = self.session.delete("{apibase}/ssh_keys/{keyid}".format(apibase=APIBASE, keyid=keyid))
        return _resp


if __name__ == "__main__":
    sys.stderr.write("This is meant for importing\n")
    sys.exit(1)
    # h=HetznerCloudConnection(debug=True)
    # h.debugprint(h.defaults)
    # h.debugprint(h.servers)
    # h.create_server(name="deployedviaapi")
