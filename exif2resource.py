#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Create a layer from a bunch of photos with exifs
#python exif2resource.py --url sandbox --login administrator --password demodemo

import requests
from requests.auth import HTTPBasicAuth

import argparse
import json,os,sys,math
from tqdm import tqdm
import exifread

parser = argparse.ArgumentParser()
parser.add_argument('--url',type=str,required=True)
parser.add_argument('--login',type=str,default='administrator')
parser.add_argument('--password',type=str)
args = parser.parse_args()

AUTH = HTTPBasicAuth(args.login, args.password)

url_base = 'https://%s.nextgis.com/' % args.url
url = url_base + 'api/resource/'

def create_layer(props):
    #create empty layer using REST API
    structure = dict()
    structure['resource']=dict()
    structure['resource']['cls']='vector_layer'
    structure['resource']['parent']=dict(id=0)
    structure['resource']['display_name']='photos with exif'
    structure['vector_layer']=dict()
    structure['vector_layer']['srs']=dict(id=3857)
    structure['vector_layer']['geometry_type']='POINT'
    structure['vector_layer']['fields']=list()
    
    for k,v in props.items():
        structure['vector_layer']['fields'].append(dict(keyname=k,datatype=v))

    response = requests.post(url, json=structure, auth = AUTH)
    vectlyr = response.json()

    if 'exception' in vectlyr.keys():
        print(vectlyr['title'])
        sys.exit()
    
    print('Layer created')

    return vectlyr

def add_attachments(fn,layer_id,feature_ngwid):
    filepath = os.path.join(data_dir,fn)
    with open(filepath, 'rb') as f:
        #upload attachment to NGW
        response = requests.put(url_base + 'api/component/file_upload/upload', data=f, auth=AUTH)
        json_data = response.json()
        json_data['filename'] = fn

        attach_data = {}
        attach_data['file_upload'] = json_data

        #add attachment to a feature
        post_url = url + layer_id +'/feature/' + feature_ngwid + '/attachment/'
        response = requests.post(post_url, data=json.dumps(attach_data), auth=AUTH)

    return response.json()

def add_feature(lon,lat,layer_id,fn):
    feature = dict()
    feature['extensions'] = dict()
    feature['extensions']['attachment'] = None
    feature['extensions']['description'] = None
    feature['fields'] = dict()
    feature['fields']['filename'] = fn
    feature['geom'] = 'POINT (%s %s)' % (lon,lat)

    post_url = url + layer_id + '/feature/?srs=4326'
    response = requests.post(post_url, data=json.dumps(feature),auth = AUTH)

    return response.json()

def _convert_to_degress(value):
    """
    Helper function to convert the GPS coordinates stored in the EXIF to degress in float format
    :param value:
    :type value: exifread.utils.Ratio
    :rtype: float
    """
    d = float(value.values[0].num) / float(value.values[0].den)
    m = float(value.values[1].num) / float(value.values[1].den)
    s = float(value.values[2].num) / float(value.values[2].den)

    return d + (m / 60.0) + (s / 3600.0)

def get_coords_from_exif(fn):
    filepath = os.path.join(data_dir,fn)
    file = open(filepath, 'rb')
    tags = exifread.process_file(file, details=False)
    file.close()

    gps_latitude = tags['GPS GPSLatitude']
    gps_latitude_ref = tags['GPS GPSLatitudeRef']
    gps_longitude = tags['GPS GPSLongitude']
    gps_longitude_ref = tags['GPS GPSLongitudeRef']

    if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
        lat = _convert_to_degress(gps_latitude)
        if gps_latitude_ref.values[0] != 'N':
            lat = 0 - lat

        lon = _convert_to_degress(gps_longitude)
        if gps_longitude_ref.values[0] != 'E':
            lon = 0 - lon
    
    return lat,lon

if __name__ == '__main__':
    data_dir = 'data'
    exifs = os.listdir(data_dir)

    props = {}
    props['filename'] = 'STRING'
    vectlyr = create_layer(props)
    layer_id = str(vectlyr['id'])

    for i in tqdm(range(len(exifs))):
        lat,lon = get_coords_from_exif(exifs[i])
        response = add_feature(lon,lat,layer_id,exifs[i])
        feature_ngwid = str(response['id'])
        response = add_attachments(exifs[i],layer_id,feature_ngwid)         
         
