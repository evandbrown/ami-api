# -*- coding: utf-8 -*-
"""
    ami-api
    ~~~~~~

    A simple, public RESTful API for listing AMIs in the public AMI catalog.
"""
from flask import Flask, Response
from flask.ext.cache import Cache
import json
import re
import boto
import conversions
from boto import ec2

application = Flask(__name__)
application.debug = False
cache = Cache(application, config={'CACHE_TYPE': 'simple'})

"""
/ lists the available regions
"""
@cache.cached(timeout=86400)
@application.route('/', methods = ['GET'])
def list_regions():
    regions = get_regions()
    js = json.dumps(regions)
    resp = Response(js, status=200, mimetype='application/json')
    return resp

"""
List the available AMI owners published by the API in the given region
"""
@application.route('/<region>', methods = ['GET'])
def list_owners(region):
    owners = [ 'amazon' ]
    js = json.dumps(owners)
    resp = Response(js, status=200, mimetype='application/json')
    return resp

"""
List the available operating systems published by the requested owner
"""
@application.route('/<region>/<owner>', methods = ['GET'])
def list_operating_systems(region, owner):
    if owner == 'amazon':
        os = [ 'linux' ]
        js = json.dumps(os)
        resp = Response(js, status=200, mimetype='application/json')
    else:
	    resp = get_404()

    return resp

"""
List the available chipset architectures given the parameters
This is the first method where AMIs are loaded from the API
"""
@application.route('/<region>/<owner>/<os>', methods = ['GET'])
def list_operating_systems_arch(region, owner, os):	
    if os == 'linux':
	    # Get all ALinux AMIS, then identify available virtualization types
        amis = get_amazon_linux_amis(region)
    else:
        resp = get_404()
    
    archs = list(set([ convert_architecture(a.architecture) for a in amis ]))
    js = json.dumps(archs)
    resp = Response(js, status=200, mimetype='application/json')

    return resp

"""
List the available virtualization types
"""
@application.route('/<region>/<owner>/<os>/<arch>', methods = ['GET'])
def list_operating_systems_arch_virttype(region, owner, os, arch):	
    if os == 'linux':
	    # Get all ALinux AMIS, then identify available boot volume types
        amis = get_amazon_linux_amis(region)
    else:
        resp = get_404()

    virt_types = list(set([ convert_virt_type(a.virtualization_type) for a in amis if a.architecture == convert_architecture(arch) ]))
    js = json.dumps(virt_types)
    resp = Response(js, status=200, mimetype='application/json')

    return resp

"""
List the available root volume types
"""
@application.route('/<region>/<owner>/<os>/<arch>/<virt_type>', methods = ['GET'])
def list_operating_systems_hypervisor_virttype(region, owner, os, arch, virt_type):	
    if os == 'linux':
	    # Get all ALinux AMIS, then identify available boot volume types
        amis = get_amazon_linux_amis(region)
    else:
        resp = get_404()

    vol_types = list(set([ convert_root_vol_type(a.root_device_type) for a in amis if a.architecture == convert_architecture(arch) and a.virtualization_type == convert_virt_type(virt_type)]))
    js = json.dumps(vol_types)
    resp = Response(js, status=200, mimetype='application/json')

    return resp

"""
List available AMIs given the parameters
"""
@application.route('/<region>/<owner>/<os>/<arch>/<virt_type>/<root_device_type>', methods = ['GET'])
def list_operating_systems_hypervisor_virttype_rootdevicetype(region, owner, os, arch, virt_type, root_device_type):	
    if os == 'linux':
	    # Get all ALinux AMIS, then identify available boot volume types
        amis = get_amazon_linux_amis(region)
    else:
        resp = get_404()

    # Filter images to only include the requested virtualization and root device types
    matching_amis = [ a for a in amis if a.architecture == convert_architecture(arch) and a.virtualization_type == convert_virt_type(virt_type) and a.root_device_type == convert_root_vol_type(root_device_type)]

    # Regex to not match AMIs with 'beta' or 'rc' in the name
    name_filter = re.compile('^(?:(?!beta|rc).)*$').search
    matching_amis = [ { 'name' : a.name, 'description' : a.description, 'image-id' : a.id }  for a in filter_list(matching_amis, name_filter) ]

    # Sort the list and get the last item
    matching_amis = sorted(matching_amis, key=lambda a: a['name'])[-1]

    js = json.dumps(matching_amis)
    resp = Response(js, status=200, mimetype='application/json')

    return resp

"""
Get all Amazon Linux AMIS
"""
def get_amazon_linux_amis(region):
    images = get_amis('amazon', region)
    return [ i for i in images if i.platform == None and i.name is not None and 'amzn-ami' in i.name ]

"""
Get all Windows Server AMIs
"""
def get_windows_server_amis(region):
    images = get_amis('amazon', region)
    return [ i for i in images if i.platform == 'windows' ]

"""
Retrieve list of AMIs for the specified owner
"""
@cache.memoize(86400)
def get_amis(owner, region):
    c = boto.ec2.connect_to_region(region)
    images = c.get_all_images(owners=[owner])
    return images

"""
Retrieve list of all regions from the EC2 API
"""
@cache.memoize(86400)
def get_regions():
    return [ r.name for r in boto.connect_ec2().get_all_regions() ]

"""
Generate a generic 404
"""
def get_404():
    return Response('Resource not found.', status=404, mimetype='text/plain')
# Start the server

"""
Regex helper method to search list of AMIs by name
"""
def filter_list(list,filter):
    return [ a for a in list for m in (filter(a.name),) if m]

"""
Convert architecture names between easy (i.e., 32/64) and official (i.e., i386/x86_64)
"""
def convert_architecture(value):
    return conversions.architectures[value]

def convert_root_vol_type(value):
    return conversions.root_device_types[value]

def convert_virt_type(value):
    return conversions.virt_types[value]

if __name__ == '__main__':
    application.run(host='0.0.0.0')