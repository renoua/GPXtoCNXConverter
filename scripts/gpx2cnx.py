import os
import math
import codecs
import xml.etree.ElementTree as ET
from xml.dom import minidom
import tkinter as tk
from tkinter import filedialog, scrolledtext
import decimal
from decimal import Decimal, getcontext


getcontext().prec = 28

# Select files and start conversion
def select_files():
    file_paths = filedialog.askopenfilenames(filetypes=[("GPX files", "*.gpx")])
    if file_paths:
        info_area.delete(1.0, tk.END)
        results = convert_gpx2cnx(list(file_paths))
        for result in results:
            info_area.insert(tk.END, result + "\n")


def prettify(elem):
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")


# Calculate 3D distance between coordinates
def calc_distance(lat1, lon1, ele1, lat2, lon2, ele2):
    R = 6371 * 1000  # Earth radius in meters
    dlat = Decimal(str(math.radians(lat2 - lat1)))
    dlon = Decimal(str(math.radians(lon2 - lon1)))
    dele = Decimal(str(ele2 - ele1))
    a = Decimal(str((math.sin(dlat/2) * math.sin(dlat/2)) + \
        (math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * \
         math.sin(dlon/2) * math.sin(dlon/2))))
    b = Decimal(str(2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))))
    h_distance = R * b
    distance = (h_distance**2 + dele**2).sqrt()  # 3D distance
    return distance


# Converts a list of GPX files to CNX xml format
def convert_gpx2cnx(gpx_files):
    output_dir= os.path.join(os.path.normpath(os.path.split(gpx_files[0])[0]),'cnx_routes')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    results = []
    for gpx_file in gpx_files:
        try:
            tree = ET.parse(gpx_file)
            root = tree.getroot()

            # Extracting waypoints
            waypoints = []
            for wpt in root.findall('{http://www.topografix.com/GPX/1/1}wpt'):
                lat = Decimal(wpt.get('lat'))
                lon = Decimal(wpt.get('lon'))
                name = wpt.find('{http://www.topografix.com/GPX/1/1}name').text \
                    if wpt.find('{http://www.topografix.com/GPX/1/1}name') is not None else ""

                waypoints.append({'lat': lat, 'lon': lon, 'name': name})

            # Extracting track points
            track_points = []
            track = root.find('{http://www.topografix.com/GPX/1/1}trk')
            if track is not None:
                track_name = track.find('{http://www.topografix.com/GPX/1/1}name').text \
                    if track.find('{http://www.topografix.com/GPX/1/1}name') is not None else "Unknown"
                trkseg = track.find('{http://www.topografix.com/GPX/1/1}trkseg')
                if trkseg is not None:
                    for trkpt in trkseg.findall('{http://www.topografix.com/GPX/1/1}trkpt'):
                        lat = Decimal(trkpt.get('lat'))
                        lon = Decimal(trkpt.get('lon'))
                        ele = Decimal(trkpt.find('{http://www.topografix.com/GPX/1/1}ele').text) \
                            if trkpt.find('{http://www.topografix.com/GPX/1/1}ele') is not None else Decimal('0.0')

                        track_points.append({'lat': lat, 'lon': lon, 'ele': ele})

            # Calc Distance, Ascent, Descent
            distance = Decimal('0.0')
            ascent = Decimal('0.0')
            descent = Decimal('0.0')
            if len(track_points) > 1:
                for i in range(1, len(track_points)):
                    lat1 = track_points[i - 1]['lat']
                    lon1 = track_points[i - 1]['lon']
                    ele1 = track_points[i - 1]['ele']
                    lat2 = track_points[i]['lat']
                    lon2 = track_points[i]['lon']
                    ele2 = track_points[i]['ele']

                    distance += calc_distance(lat1, lon1, ele1, lat2, lon2, ele2)
                    ele_diff = ele2 - ele1

                    if ele_diff > 0:
                        ascent += ele_diff
                    else:
                        descent += ele_diff

                    distance = distance.quantize(Decimal('1.00'), decimal.ROUND_HALF_UP)
                    ascent = ascent.quantize(Decimal('1.00'), decimal.ROUND_HALF_UP)
                    descent = descent.quantize(Decimal('1.00'), decimal.ROUND_HALF_UP)

            # Calc Track - Relative Coordinates
            if track_points:
                first_lat = track_points[0]['lat']
                first_lon = track_points[0]['lon']
                first_ele = (track_points[0]['ele'] * 100).quantize(Decimal('1'), decimal.ROUND_HALF_UP)

                relative_points = [f"{first_lat},{first_lon},{first_ele}"] # First Point - Absolute Coordinates

                first_diffs = []
                for i in range(1, len(track_points)): # Calc first diffs
                    lat1 = track_points[i-1]['lat']
                    lon1 = track_points[i-1]['lon']
                    lat2 = track_points[i]['lat']
                    lon2 = track_points[i]['lon']

                    lat_diff = (lat2 - lat1) * 10000000
                    lon_diff = (lon2 - lon1) * 10000000
                    ele_diff = track_points[i]['ele'] * 100 - track_points[i-1]['ele'] * 100

                    first_diffs.append((lat_diff, lon_diff, ele_diff))

                    if i == 1: # Second Point
                        lat_diff = lat_diff.quantize(Decimal('1'), decimal.ROUND_HALF_UP)
                        lon_diff = lon_diff.quantize(Decimal('1'), decimal.ROUND_HALF_UP)
                        ele_diff = ele_diff.quantize(Decimal('1'), decimal.ROUND_HALF_UP)

                        relative_points.append(f"{lat_diff},{lon_diff},{ele_diff}")

                for i in range(1, len(first_diffs)): # Calc second diffs
                    lat_diff = (first_diffs[i][0] - first_diffs[i-1][0]).quantize(Decimal('1'), decimal.ROUND_HALF_UP)
                    lon_diff = (first_diffs[i][1] - first_diffs[i-1][1]).quantize(Decimal('1'), decimal.ROUND_HALF_UP)
                    ele_diff = (first_diffs[i][2]).quantize(Decimal('1'), decimal.ROUND_HALF_UP)

                    relative_points.append(f"{lat_diff},{lon_diff},{ele_diff}")

            # Create XML
            route = ET.Element('Route')
            ET.SubElement(route, 'Id').text = track_name  # Use track name as Id
            ET.SubElement(route, 'Distance').text = f'{distance}'

            duration = ET.SubElement(route, 'Duration')
            duration.text = '\n  '

            ET.SubElement(route, 'Ascent').text = f'{ascent}'
            ET.SubElement(route, 'Descent').text = f'{descent}'
            ET.SubElement(route, 'Encode').text = '2'
            ET.SubElement(route, 'Lang').text = '0'
            ET.SubElement(route, 'TracksCount').text = str(len(track_points))

            if relative_points:
                tracks_str = ';'.join(relative_points)
                ET.SubElement(route, 'Tracks').text = tracks_str
            else:
                ET.SubElement(route, 'Tracks').text = ""

            ET.SubElement(route, 'Navs')
            ET.SubElement(route, 'PointsCount').text = str(len(waypoints))

            points = ET.SubElement(route, 'Points')
            for wpt in waypoints:
                point = ET.SubElement(points, 'Point')
                ET.SubElement(point, 'Lat').text = str(wpt['lat'])
                ET.SubElement(point, 'Lng').text = str(wpt['lon'])
                ET.SubElement(point, 'Type').text = '0' # Type 0 - point marker without differentiation by purpose
                ET.SubElement(point, 'Descr').text = wpt['name']

            filename = os.path.splitext(os.path.basename(gpx_file))[0]
            trim_filename = filename[:18]
            output_filename = os.path.join(output_dir, f"route_{trim_filename}.cnx")
            xml_string = prettify(route)
            with codecs.open(output_filename, "w", encoding='utf-8-sig') as f:
                f.write('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n')
                f.write(xml_string[xml_string.find('<Route'):])

            results.append(f"-- {filename} -> SUCCESS")
        except Exception as e:
            results.append(f"ERROR - file {gpx_file}: {e}")
    return results


# Create GUI
root = tk.Tk()
root.title("GPXtoCNX Converter")

button = tk.Button(root, text="Browse files", command=select_files)
button.pack(pady=10)

info_area = scrolledtext.ScrolledText(root, width=80, height=20)
info_area.pack(pady=10)

root.mainloop()