#!/usr/bin/env python3
# this is just an attempt to get familiar with the Hetzner DNS api
# ultimately the api calls will be moved to the api lib
# Todo: Tests

import requests
import argparse
import os
import sys

apiversion = "v1"
apibase = 'https://dns.hetzner.com/api/{version}'.format(version=apiversion)


def debugprint(msg):
    if args.debug:
        sys.stderr.write("{msg}\n".format(msg=msg))


def mkrequest(method="get", path="", additional_headers={}):
    """creates request towards path, return type based on content-type"""
    default_headers = {'Auth-API-Token': token, 'charset': 'utf-8'}
    if additional_headers:
        default_headers.update(additional_headers)
    if method == "get":
        _action = requests.get
    elif method == "post":
        _action = requests.post
    _resp = _action(url="{apibase}/{path}".format(apibase=apibase, path=path),
                        headers=default_headers)
    _resp.raise_for_status()
    if default_headers['Content-Type'] == 'application/json':
        return _resp.json()
    else:
        return _resp.text


def handle_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--outputfile",
                        help="outputfile name, default is stdout")
    parser.add_argument("-O", "--outputdir",
                        help="dir for batch output, implies --all")
    parser.add_argument("-d", "--debug",
                        help="debug mode", action="store_true", default=False)
    parser.add_argument("-z", "--zone",
                        help="Name of zone to be exported")
    parser.add_argument("-a", "--all",
                        help="export all zones", action="store_true",
                        default=False)
    _args = parser.parse_args()
    return _args


def get_all_zones():
    """returns a list of dicts"""
    _resp = mkrequest(
        method="get", path='zones',
        additional_headers={'Content-Type': 'application/json'}
        )
    _zones = _resp['zones']
    debugprint("found {num_zones} zones".format(num_zones=len(_zones)))
    return _zones


def export_zone(zone_id):
    _resp = mkrequest(
        path="/zones/{zone_id}/export".format(zone_id=zone_id),
        additional_headers={
            'Content-Type': 'application/x-www-form-urlencoded'
            }
        )
    return _resp


def get_zone_id(zone_name):
    for zone in zones:
        if zone['name'] == zone_name:
            debugprint("Found id {zone_id} for zone {zone_name}".format(
                zone_id=zone['id'],
                zone_name=zone_name)
                )
            return zone['id']
        else:
            next
    debugprint("Zone {zone_name} not found".format(zone_name=zone_name))
    return False


if __name__ == "__main__":
    args = handle_args()
    try:
        token = os.environ['HCLOUD_DNS_TOKEN']
    except KeyError:
        sys.stderr.write("missing env var HCLOUD_DNS_TOKEN\n")
        sys.exit(1)
    zones = get_all_zones()
    if args.outputdir:
        debugprint("Option --outputdir supplied, assuming option --all")
        for zone in zones:
            zone_name = zone['name']
            zone_id = zone['id']
            with open('{outputdir}/{zone_name}.zone'.format(
                    outputdir=args.outputdir,
                    zone_name=zone_name), 'w') as outfile:
                debugprint(
                    "exporting zone {zone_name}".format(zone_name=zone_name)
                    )
                zone_content = export_zone(zone_id)
                outfile.write(zone_content)
        sys.exit(0)
    # set stdout to output file handle
    if args.outputfile:
        outfile = open(args.outputfile, 'w')
        original_stdout = sys.stdout
        sys.stdout = outfile

    if args.all:
        for zone in zones:
            print(export_zone(zone['id']))
    elif args.zone:
        _zone_id = get_zone_id(args.zone)
        if _zone_id:
            print(export_zone(_zone_id))
        else:
            sys.stderr.write("Zone {zone_name} not found\n".format(
                zone_name=args.zone)
                )
    # reset stdout
    if args.outputfile:
        sys.stdout = original_stdout
