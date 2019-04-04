from __future__ import print_function
from flask import Flask, render_template
import json
from flask import request, redirect, url_for
import urllib
import requests
import shutil
import os
import math
from multiprocessing import Process

class Map(object):
    def __init__(self):
        self._points = []
        self._dpoint = []
    def add_point(self, coordinates):
        self._points.append(coordinates)
    def give_point(self,point):
        self._dpoint.append(point)
    def clear_points(self):
        self._points.clear()


    def __str__(self):
        dwld_centerLat = self._dpoint[0][0]
        dwld_centerLon = self._dpoint[0][1]
        # markersCode = "\n".join(
        #     [ """new google.maps.Marker({{
        #         position: new google.maps.LatLng({lat}, {lon}),
        #         map: map
        #         }});""".format(lat=x[0], lon=x[1]) for x in self._points
        #     ])
        activity_coordinates = ",\n".join(
                ["{{lat:{centerLat}, lng:{centerLon}, heading:{heading}}}".format(centerLat=x[0], centerLon=x[1], heading=x[2]) for x in self._points])


        return """
            <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.1.0/jquery.min.js"></script>
            <script src="https://maps.googleapis.com/maps/api/js?key=AIzaSyCf5FVJ_PzIUFf5loz7T2JBgMjWUYOPumI&callback=initialize"></script>
            <!-- <meta http-equiv="refresh" content="10" > -->
            <div id="pano" style="height: 100%; width: 100%"></div>
            <div id="map-canvas" style="height: 100%; width: 100%"></div>

            <div id="download">
            <button id="doer" onclick="doThings()">Download</button>
            </div>


            <script type="text/javascript">
                var map;
                var path;
                var metadata;
                var API_KEY = "AIzaSyCf5FVJ_PzIUFf5loz7T2JBgMjWUYOPumI"
                var activity_coordinates = [{activity_coordinates}]
                var pano_name;
                var heading_1;
                var heading_2;
                var cur_lat;
                var cur_lng;

                function getMetadata() {{
	                // ajax the JSON to the server
	                $.post("/postmeta", {{metadata,path,pano_name,heading_1, heading_2, cur_lat, cur_lng}}, function(){{
                }});
                }}

                function shutdown() {{
                    $.post("/shutdown", "Done", function(){{
                    }});
                }}



                function show_map(loc) {{
                    map = new google.maps.Map(document.getElementById("map-canvas"), {{
                        zoom: 18,
                        //center: new google.maps.LatLng({centerLat}, {centerLon})
                        center: new google.maps.LatLng(loc['lat'], loc['lng'])
                    }});

                    //var location = {{lat:{centerLat}, lng:{centerLon}}};
                    //console.log(location)
                    var panorama = new google.maps.StreetViewPanorama(
                    document.getElementById('pano'));
                    panorama.setPosition(loc);

                     google.maps.event.addListener(panorama, 'links_changed', function() {{
                         var links =  panorama.getLinks();
                         var j;
                         if(loc['heading'] == -1) {{
                             panorama.setPov({{
                                 heading: links[0].heading,
                                 pitch: 0,
                                 zoom: 1
                             }});

                            cur_lat = loc['lat']
                            cur_lng = loc['lng']
                            heading_1 = links[0].heading
                            heading_2 = links[1].heading
                            pano_name = links[0].pano
                            path = "https://maps.googleapis.com/maps/api/streetview?size=640x480" +"&pano=" + panorama.getPano() + "&heading=" + links[0].heading + "&pitch=" + panorama.getPov().pitch + "&key=" + API_KEY;
                            metadata = "https://maps.googleapis.com/maps/api/streetview/metadata?size=640x480" +"&pano=" + panorama.getPano() + "&heading=" + links[0].heading + "&pitch=" + panorama.getPov().pitch + "&key=" + API_KEY;
                            getMetadata();

                        }} else {{
                             panorama.setPov({{
                                 heading: loc['heading'],
                                 pitch: 0,
                                 zoom: 1
                             }});

                            cur_lat = loc['lat']
                            cur_lng = loc['lng']
                            heading_1 = links[0].heading
                            heading_2 = links[1].heading
                            pano_name = links[0].pano
                            path = "https://maps.googleapis.com/maps/api/streetview?size=640x480" +"&pano=" + panorama.getPano() + "&heading=" + loc['heading'] + "&pitch=" + panorama.getPov().pitch + "&key=" + API_KEY;
                            metadata = "https://maps.googleapis.com/maps/api/streetview/metadata?size=640x480" +"&pano=" + panorama.getPano() + "&heading=" + loc['heading'] + "&pitch=" + panorama.getPov().pitch + "&key=" + API_KEY;
                            getMetadata();
                        }}
                    }});
                map.setStreetView(panorama);
                }}

                function initialize() {{
                var i;
                //console.log(activity_coordinates)
                for (i=0;i<activity_coordinates.length;i++){{
                var loc = activity_coordinates[i]
                show_map(loc)
                }}
            }}


                // Download the image manually //

                function doThings() {{
                    var location = {{lat:{centerLat}, lng:{centerLon}}};
                    var panorama = new google.maps.StreetViewPanorama(
                    document.getElementById('pano'));
                    panorama.setPosition(location);

                    google.maps.event.addListener(panorama, 'links_changed', function() {{
                    var links1 =  panorama.getLinks();

                    panorama.setPov({{
                    heading: links1[0].heading,
                    pitch: 0,
                    zoom: 1
                    }});

                var panoID = panorama.getPano();
                //document.getElementById("download").innerHTML = "https://maps.googleapis.com/maps/api/streetview?size=640x480" +"&pano=" + panoID + "&heading=" + links1[0].heading + "&pitch=" + panorama.getPov().pitch + "&key=AIzaSyCf5FVJ_PzIUFf5loz7T2JBgMjWUYOPumI";
                //use the next line to open in a new tab the resulting image at max size (640x640)
                path = "https://maps.googleapis.com/maps/api/streetview?size=640x480" +"&pano=" + panoID + "&heading=" + links1[0].heading + "&pitch=" + panorama.getPov().pitch + "&key=" + API_KEY;
                metadata = "https://maps.googleapis.com/maps/api/streetview/metadata?size=640x480" +"&pano=" + panoID + "&heading=" + links1[0].heading + "&pitch=" + panorama.getPov().pitch + "&key=" + API_KEY;
                //window.open(metadata);
                //window.open(path);
                getMetadata();
                }});
            }}

            google.maps.event.addDomListener(window, 'load', initialize);
            </script>
        """.format(activity_coordinates=activity_coordinates,centerLat=dwld_centerLat,centerLon=dwld_centerLon)
        #format(centerLat=centerLat, centerLon=centerLon)

def download(url, file_path):
  r = requests.get(url, stream=True)
  if r.status_code == 200: # if request is successful
    with open(file_path, 'wb') as f:
        r.raw.decode_content = True
        shutil.copyfileobj(r.raw, f)
        return "Downloaded"

app = Flask(__name__)

@app.route('/')
def home():
    return render_template("output.html")

def coordinate_offset(orig_lat, orig_long, heading_1, heading_2):
    f = open('changed_coordinates.data', 'a')
    total_offset = 0.000195
    heading_1 = float(heading_1)
    heading_2 = float(heading_2)
    terminal = heading_1 % 90
    quad = int(heading_1//90)
    if quad == 0 or quad == 2:
        terminal = 90-terminal
    long_offset = total_offset*math.cos(terminal*math.pi/180)
    lat_offset = total_offset*math.sin(terminal*math.pi/180)
    if quad == 1:
        lat_offset = -lat_offset
    elif quad == 2:
        long_offset = -long_offset
        lat_offset = -lat_offset
    elif quad == 3:
        long_offset = -long_offset
    f.write(f'{float(orig_lat)+lat_offset} {float(orig_long)+long_offset} {heading_2}\n')
    print(f'new lat: {float(orig_lat)+lat_offset}, new_long: {float(orig_long)+long_offset}')
    print(f'view heading: {heading_2}')

    terminal = heading_2 % 90
    quad = int(heading_2//90)
    if quad == 0 or quad == 2:
        terminal = 90-terminal
    long_offset = total_offset*math.cos(terminal*math.pi/180)
    lat_offset = total_offset*math.sin(terminal*math.pi/180)
    if quad == 1:
        lat_offset = -lat_offset
    elif quad == 2:
        long_offset = -long_offset
        lat_offset = -lat_offset
    elif quad == 3:
        long_offset = -long_offset
    f.write(f'{float(orig_lat)+lat_offset} {float(orig_long)+long_offset} {heading_1}\n')
    print(f'new lat: {float(orig_lat)+lat_offset}, new_long: {float(orig_long)+long_offset}')
    print(f'view heading: {heading_1}')


@app.route('/postmeta', methods = ['POST'])
def get_meta_data():
    data = request.form["metadata"]
    path = request.form["path"]
    pano_name = request.form["pano_name"]
    heading_1 = request.form["heading_1"]
    heading_2 = request.form["heading_2"]
    lat = request.form["cur_lat"]
    lng = request.form["cur_lng"]
    print(f'lat: {lat}, long: {lng}, heading_1: {heading_1}, heading_2: {heading_2}')

    if orig_coord_eval is True:
        coordinate_offset(lat, lng, heading_1, heading_2)

    metadata = requests.get(data, stream=True).json()
    if metadata['status'] == "OK":
        dir_path = "./downloaded_images"
        file_path = os.path.join(dir_path, 'gsv_' + str(pano_name) + '.jpg')
        res = download(path,file_path)
        return res

    elif metadata['status'] == "REQUEST_DENIED":
        print("API KEY may not be activated or authorized with the project")
        return 0
    else:
        return "Image Status not OK"

@app.route('/shutdown', methods = ['POST'])
def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    return "Shutdown"


# @app.route('/postimg', methods = ['POST'])
# def get_image():
#     data = request.form["path"]
#     print(data)
#     return str(data)

map = Map()
orig_coord_eval = True

if __name__ == "__main__":
    if os.stat('changed_coordinates.data').st_size == 0:
        f1 = open('stop-sign-coordinates.data', 'r')
        lat_list = []
        long_list = []
        heading_list = []
        for line in f1:
            if 'lat' in line:
                lat_idx = line.find('lat')+5
                lng_idx = line.find('lon')+5
                latitude = float(line[lat_idx:lat_idx+10])
                longitude = float(line[lng_idx:lng_idx+12])
                lat_list.append(latitude)
                long_list.append(longitude)
                heading_list.append(-1)
        aug_points = list(zip(lat_list, long_list, heading_list))
        #points = [(29.7209117,-95.427386),(29.712817,-95.4248398),(29.7209575,-95.4280115),(29.7112592,-95.428755),(29.7107108,-95.4287406)]
        for i in aug_points:
            map.add_point(i)
            map.give_point((29.7002875,-95.5196913,)) # dummy coordinates
        with open("./templates/output.html", "w") as out:
            print(map, file=out)
        app.run(debug=True)
    else:
        f2 = open('changed_coordinates.data', 'r')
        lat_list = []
        long_list = []
        heading_list = []
        for line in f2:
            elem = line.split()
            latitude = float(elem[0])
            longitude = float(elem[1])
            heading = float(elem[2])
            lat_list.append(latitude)
            long_list.append(longitude)
            heading_list.append(heading)
        aug_points = list(zip(lat_list, long_list, heading_list))
        for i in aug_points:
            map.add_point(i)
            map.give_point((29.7002875,-95.5196913,))
        with open("./templates/output.html", "w") as out:
            orig_coord_eval = False
            print(map, file=out)
        app.run(debug=True)
