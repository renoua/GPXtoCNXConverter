# gpx2cnx.py
import os
import math
import codecs
import xml.etree.ElementTree as ET
from xml.dom import minidom
import tkinter as tk
from tkinter import filedialog, scrolledtext
import decimal
from decimal import Decimal, getcontext
import src.poi_types_editor as PE


getcontext().prec = 28


class GPX2CNX:
    # Creating GUI and calling button functions
    def __init__(self, root):
        self.root = root
        root.title("GPXtoCNX Converter")

        self.status_label = tk.Label(root, text="", width=30)
        self.status_label.grid(row=4, column=1, columnspan=3, sticky="ew", padx=25, pady=5)

        self.button1 = tk.Button(root, text="GPX -> CNX", command=lambda:[self.status_label.config(text=""), self.select_files()])
        self.button1.grid(row=1, column=1, columnspan=1, sticky="ew", padx=25, pady=5)

        self.button2 = tk.Button(root, text="POI TYPES EDITOR", command=self.poi_editor)
        self.button2.grid(row=2, column=1, columnspan=1, sticky="ew", padx=25, pady=5)

        self.button3 = tk.Button(root, text="Log", command=self.log_window)
        self.button3.grid(row=3, column=1, columnspan=1, sticky="ew", padx=25, pady=5)

        root.grid_columnconfigure(1, weight=1)

    def logging(self):
        log = "gpx2cnx.py log"
        for result in self.results:
            log = log + "\n" + result
        try:
            with open("log.txt", "w", encoding="utf8") as logtxt:
                logtxt.write(log + "\n")
        except Exception as e:
            self.status_label.config(text="* Error write log *")
        if self.rstat == 1:
            self.status_label.config(text="* DONE *")
        else:
            self.status_label.config(text="* ERROR *")

    # Run POI Types Editor
    def poi_editor(self):
        window = tk.Toplevel()
        PE.POIEditor(window)
        window.grab_set()

    # log_window
    def log_window(self):
        textinfo = ""
        flogout = 0
        try:
            with open("log.txt", "r") as logtxt:
                textinfo = logtxt.read()
                flogout = 1
        except FileNotFoundError:
            self.status_label.config(text="* File not found *")
        except Exception as e:
            self.status_label.config(text="* Error read log *")

        if flogout == 1:
            loginfo = tk.Toplevel()
            loginfo.title("Log")
            info_area = scrolledtext.ScrolledText(loginfo, width=80, height=20)
            info_area.pack(pady=10)
            loginfo.grab_set()

            info_area.insert(tk.END, textinfo)

    # Select files and start conversion
    def select_files(self):
        file_paths = filedialog.askopenfilenames(filetypes=[("GPX files", "*.gpx")])
        if file_paths:
            self.convert_gpx2cnx(list(file_paths))

    def prettify(self, elem):
        rough_string = ET.tostring(elem, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")

    # Calculate 3D distance between coordinates
    def calc_distance(self):
        R = 6371 * 1000  # Earth radius in meters
        dlat = Decimal(str(math.radians(self.lat2 - self.lat1)))
        dlon = Decimal(str(math.radians(self.lon2 - self.lon1)))
        dele = Decimal(str(self.ele2 - self.ele1))
        a = Decimal(str((math.sin(dlat/2) * math.sin(dlat/2)) +
            (math.cos(math.radians(self.lat1)) * math.cos(math.radians(self.lat2)) *
             math.sin(dlon/2) * math.sin(dlon/2))))
        b = Decimal(str(2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))))
        h_distance = R * b
        distance = (h_distance**2 + dele**2).sqrt()  # 3D distance
        return distance

    # Converts a list of GPX files to CNX xml format
    def convert_gpx2cnx(self, gpx_files):
        output_dir= os.path.join(os.path.normpath(os.path.split(gpx_files[0])[0]),'cnx_routes')
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        log = "gpx2cnx.py log"
        self.results = []
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
                        self.lat1 = track_points[i - 1]['lat']
                        self.lon1 = track_points[i - 1]['lon']
                        self.ele1 = track_points[i - 1]['ele']
                        self.lat2 = track_points[i]['lat']
                        self.lon2 = track_points[i]['lon']
                        self.ele2 = track_points[i]['ele']

                        distance += self.calc_distance()
                        ele_diff = self.ele2 - self.ele1

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
                xml_string = self.prettify(route)
                with codecs.open(output_filename, "w", encoding='utf-8-sig') as f:
                    f.write('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n')
                    f.write(xml_string[xml_string.find('<Route'):])

                self.results.append(f"-- {gpx_file} -> SUCCESS")
                self.rstat = 1
            except Exception as e:
                self.results.append(f"ERROR - file {gpx_file}: {e}")
                self.rstat = 0
                self.logging()
            self.logging()
        return self.results


# Run app
if __name__ == "__main__":
    root = tk.Tk()
    app = GPX2CNX(root)
    root.mainloop()
