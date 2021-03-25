#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from requests.auth import HTTPBasicAuth

import argparse
import json,os
from tqdm import tqdm

#python attach2resource.py --url sandbox --login admin --password demodemo

parser = argparse.ArgumentParser()
parser.add_argument('--url',type=str,required=True)
parser.add_argument('--login',type=str,default='administrator')
parser.add_argument('--password',type=str)
parser.add_argument('--debug', '-d', help='debug mode', action='store_true')

args = parser.parse_args()

if args.login and args.password:
    AUTH = HTTPBasicAuth(args.login, args.password)
else:
    AUTH = ''

url_base = 'https://%s.nextgis.com/' % args.url
url = url_base + 'api/resource/'

def lon_3857(x):
    return earthRadius * math.radians(x)

def lat_3857(y):
    return earthRadius * math.log(math.tan(math.pi / 4 + math.radians(y) / 2))


def create_layer():
    #create empty layer using REST API
    structure = dict()
    structure['resource']=dict()
    structure['resource']['cls']='vector_layer'
    structure['resource']['parent']=dict(id=0)
    structure['resource']['display_name']='photos'
    structure['vector_layer']=dict()
    structure['vector_layer']['srs']=dict(id=3857)
    structure['vector_layer']['geometry_type']='POINT'
    structure['vector_layer']['fields']=list()
    structure['vector_layer']['fields'].append(dict(keyname='datetime',datatype='STRING'))

    response = requests.post(url, json=structure, auth = AUTH)
    vectlyr = response.json()
    print('Layer created')
    if args.debug: print(url)

    return vectlyr

def add_feature(lon,lat,datetime,layer_id):
    #add feature with attachements

    ngwFeature = dict()
    ngwFeature['extensions'] = dict()
    ngwFeature['extensions']['attachment'] = None
    ngwFeature['extensions']['description'] = None
    ngwFeature['fields'] = dict()
    ngwFeature['fields']['datetime'] = datetime
    ngwFeature['geom'] = 'POINT (%s %s)' % (lon,lat) #no reproject, coords are 3857 already

    post_url = url + layer_id + '/feature/'
    response = requests.post(post_url, data=json.dumps(ngwFeature),auth = AUTH)

    return response.json()

def add_attachments(attaches,layer_id,feature_ngwid,feature_id):
    for attach in attaches:
        filepath = os.path.join(data_dir,feature_id,attach)
        with open(filepath, 'rb') as f:
            #upload attachment to NGW
            response = requests.put(url_base + 'api/component/file_upload/upload', data=f, auth=AUTH)
            json_data = response.json()
            json_data['name'] = attach

            attach_data = {}
            attach_data['file_upload'] = json_data

            #add attachment to a feature
            post_url = url + layer_id +'/feature/' + feature_ngwid + '/attachment/'
            response = requests.post(post_url, data=json.dumps(attach_data), auth=AUTH)

    return response.json()

if __name__ == '__main__':
    data_dir = 'data'
    f_input_name = 'form.geojson'
    
    vectlyr = create_layer()
    layer_id = str(vectlyr['id']) #str(6301) #str(vectlyr['id'])

    with open(os.path.join(data_dir,f_input_name), 'r', encoding='UTF-8') as data_file:
        data = json.load(data_file)
        
        features = data['features']
        for i in tqdm(range(len(features))):
            feature = data['features'][i]
            lon = feature['geometry']['coordinates'][0]
            lat = feature['geometry']['coordinates'][1]
            datetime = feature['properties']['field_4']
            response = add_feature(lon,lat,datetime,layer_id)
            feature_ngwid = str(response['id'])
            feature_id = str(feature['properties']['_id'])
            attaches = feature['properties']['attaches']
            if len(attaches) > 0:
                response = add_attachments(attaches,layer_id,feature_ngwid,feature_id)            
