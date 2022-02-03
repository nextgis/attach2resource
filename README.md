# attach2resource
Send a bunch of attachments (usually photos) to a vector layer. 

Creates a layer and attachmets from a GeoJSON file + attachments exported from NextGIS Mobile/Collector:

    python attach2resource.py --url sandbox --login administrator --password demodemo
    
Works under Python 2.7.x and Python 3.7.x

Params:

    * url - subdomain name of your Web GIS url. If your Web GIS is example.nextgis.com use 'example' here.

See also: https://github.com/nextgis/helper_scripts/tree/master/photos2ngw
