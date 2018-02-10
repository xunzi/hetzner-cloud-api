#!/usr/bin/env python3

import requests
import sys
import os

APIVERSION = "v1"
APIBASE = "https://api.hetzner.cloud/{0}".format(APIVERSION) 



class HetznerCloudConnection:
    def __init__(self, debug=False):
        self. debug = debug
        self.session = requests.Session()
        try:
            self.token = os.environ['API_TOKEN']
        except KeyError:
            sys.stderr.write("Missing env var API_TOKEN\n")
            sys.exit(1)
        self.session.headers = { "Authorization": "Bearer {0}".format(self.token) }
        self.servers = []
        self.sshkeys = []
        self.get_servers()
        self.get_sshkeys()
        self.defaults = {
            'ssh_keys': [],
            'server_type': 'cx11',
            'image': 'ubuntu-16.04'
            }
        if len(self.sshkeys) == 1:
            self.defaults['ssh_keys'].append(self.sshkeys[0]['id'])
        
    def debugprint(self, msg):
        if self.debug:
            sys.stderr.write("{0}\n".format(msg))

    def get(self, path):
        _resp = self.session.get("{0}/{1}".format(APIBASE, path))
        self.debugprint(_resp.text)
        return _resp.json()[path]
        
    def post(self,path, payload = {}):
        self.session.headers.update({"Content-Type": "application/json"})
        _resp = self.session.post("{0}/{1}".format(APIBASE, path), json = payload)
        self.debugprint(_resp.text)
        return _resp

    def delete(self,server_id):
        s.headers.update({"Content-Type": "application/json"})
        _resp = s.delete("{0}/servers/{1}".format(APIBASE, server_id))
        self.debugprint(_resp.text)
        return _resp

    def get_servers(self):
        _resp = self.get("servers")
        for _s in _resp:
            self.servers.append(_s)
        self.debugprint("Found {0} servers".format(len(self.servers)))
        for _s in self.servers:
            self.debugprint("{0} - {1} - {2}".format(_s['id'], _s['name'], _s['public_net']['ipv4']['ip']))

    def get_sshkeys(self):
        _resp = self.get("ssh_keys")
        #self.debugprint(_resp)
        for _key in _resp:
            self.sshkeys.append(_key)
        self.debugprint("Found {0} keys".format(len(self.sshkeys)))
        for _key in self.sshkeys:
            self.debugprint("Key id {0}, name {1}, fingerprint {2}".format(_key['id'], _key['name'], _key['fingerprint']))

    def create_server(self, name = ""):
        server_spec = self.defaults
        if name:
            server_spec['name'] = name
        _resp = self.post("servers", payload = server_spec)
        self.debugprint(_resp)
        
if __name__ == "__main__":

    h = HetznerCloudConnection(debug=True)
    h.debugprint(h.defaults)
    h.debugprint(h.servers)
    #h.create_server(name="deployedviaapi")
    
