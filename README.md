# Set of scripts to turn photos into NGW vector layer

## exif2resource.py

Creates a layer from a bunch of photos with exifs. Each photo - a point with attached photo. Put data in 'data' folder.
Requires: exifread, tqdm

    python exif2resource.py --url sandbox --login administrator --password demodemo

## attach2resource.py

Creates a layer and attachments from a GeoJSON file + attachments exported from NextGIS Mobile/Collector.
Requires: tqdm

    python attach2resource.py --url sandbox --login administrator --password demodemo

Params:

    * url - subdomain name of your Web GIS url. If your Web GIS is example.nextgis.com use 'example' here.

## See also

* https://github.com/nextgis/helper_scripts/tree/master/photos2ngw
