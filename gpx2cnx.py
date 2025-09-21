#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import uuid
import xml.etree.ElementTree as ET
from xml.dom.minidom import parseString
import random
import os
import math
import codecs
import tkinter as tk
from tkinter import filedialog
from decimal import Decimal, getcontext, ROUND_HALF_UP


getcontext().prec = 28

class GPX2CNX:
    # Creating GUI and calling button functions
    def __init__(self, root):
        self.root = root
        root.title("GPXtoCNX Converter")

        self.status_label = tk.Label(root, text="", width=30)
        self.status_label.grid(row=4, column=1, columnspan=3, sticky="ew", padx=25, pady=5)

        self.leader_time_entry = tk.Entry(root, width=30)
        self.leader_time_entry.grid(row=0, column=1, columnspan=2, sticky="ew", padx=25, pady=5)
        self.leader_time_entry.insert(0, "0")

        self.button1 = tk.Button(root, text="GPX -> CNX", command=lambda: [self.status_label.config(text=""), self.select_files()])
        self.button1.grid(row=1, column=1, columnspan=1, sticky="ew", padx=25, pady=5)

        root.grid_columnconfigure(1, weight=1)

    # Select files and start conversion
    def select_files(self):
        file_paths = filedialog.askopenfilenames(filetypes=[("GPX files", "*.gpx")])
        if file_paths:
            self.convert_gpx2cnx(list(file_paths))
           
    def compute_leader_times(self, total_secs: int, num_points: int) -> str:
        segments = num_points - 1
        times = [0] * segments
        for i in range(total_secs):
            times[i % segments] += 1
        random.shuffle(times)
        return "0;" + ";".join(str(t) for t in times) + ";"

    def make_pretty_xml(self, root: ET.Element) -> str:
        raw = ET.tostring(root, encoding='utf-8')
        dom = parseString(raw)
        pretty = dom.toprettyxml(indent="  ", encoding='utf-8').decode('utf-8')
        lines = [l for l in pretty.splitlines() if l.strip()]
       # Retirer la déclaration auto générée
        if lines and lines[0].startswith("<?xml"):
            lines.pop(0)
        header = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        return header + "\n" + "\n".join(lines) + "\n"


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
        output_dir = os.path.join(os.path.normpath(os.path.split(gpx_files[0])[0]), 'cnx_routes')
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        for gpx_file in gpx_files:
            try:
                tree = ET.parse(gpx_file)
                root = tree.getroot()

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

                point_dist_list = []
                point_dist_list.append(0)
                
                if len(track_points) > 1:
                    for i in range(1, len(track_points)):
                        self.lat1 = track_points[i - 1]['lat']
                        self.lon1 = track_points[i - 1]['lon']
                        self.ele1 = track_points[i - 1]['ele']
                        self.lat2 = track_points[i]['lat']
                        self.lon2 = track_points[i]['lon']
                        self.ele2 = track_points[i]['ele']

                        dist=self.calc_distance()
                        point_dist_list.append(int((dist * Decimal('100')).to_integral_value(rounding=ROUND_HALF_UP)))
                        distance += dist
                        
                        ele_diff = self.ele2 - self.ele1
                        if ele_diff > 0:
                            ascent += ele_diff
                        else:
                            descent += ele_diff

                    distance = distance.quantize(Decimal('1.00'), ROUND_HALF_UP)
                    ascent = ascent.quantize(Decimal('1.00'), ROUND_HALF_UP)
                    descent = descent.quantize(Decimal('1.00'), ROUND_HALF_UP)

                # Calc Track - Relative Coordinates
                if track_points:
                    first_lat = track_points[0]['lat']
                    first_lon = track_points[0]['lon']
                    first_ele = (track_points[0]['ele'] * 100).quantize(Decimal('1'), ROUND_HALF_UP)

                    relative_points = [f"{first_lat},{first_lon},{first_ele}"]  # First Point - Absolute Coordinates

                    first_diffs = []
                    for i in range(1, len(track_points)):  # Calc first diffs
                        lat1 = track_points[i-1]['lat']
                        lon1 = track_points[i-1]['lon']
                        lat2 = track_points[i]['lat']
                        lon2 = track_points[i]['lon']

                        lat_diff = (lat2 - lat1) * 10000000
                        lon_diff = (lon2 - lon1) * 10000000
                        ele_diff = track_points[i]['ele'] * 100 - track_points[i-1]['ele'] * 100

                        first_diffs.append((lat_diff, lon_diff, ele_diff))

                        if i == 1:  # Second Point
                            lat_diff = lat_diff.quantize(Decimal('1'), ROUND_HALF_UP)
                            lon_diff = lon_diff.quantize(Decimal('1'), ROUND_HALF_UP)
                            ele_diff = ele_diff.quantize(Decimal('1'), ROUND_HALF_UP)

                            relative_points.append(f"{lat_diff},{lon_diff},{ele_diff}")

                    for i in range(1, len(first_diffs)):  # Calc second diffs
                        lat_diff = (first_diffs[i][0] - first_diffs[i-1][0]).quantize(Decimal('1'), ROUND_HALF_UP)
                        lon_diff = (first_diffs[i][1] - first_diffs[i-1][1]).quantize(Decimal('1'), ROUND_HALF_UP)
                        ele_diff = (first_diffs[i][2]).quantize(Decimal('1'), ROUND_HALF_UP)

                        relative_points.append(f"{lat_diff},{lon_diff},{ele_diff}")


                filename = os.path.splitext(os.path.basename(gpx_file))[0]
                trim_filename = filename[:18]

                random_id = random.randint(10000, 99999)
                
                # Create XML
                
                root = ET.Element("segment")
                head = ET.SubElement(root, "head")

                ET.SubElement(head, "name").text = trim_filename
                ET.SubElement(head, "uuid").text = str(uuid.uuid4())
                ET.SubElement(head, "num_id").text = str(random_id)
                ET.SubElement(head, "manufacturer_id").text = "115"
                ET.SubElement(head, "sport").text = "2"
                ET.SubElement(head, "start_position").text = f"{first_lat},{first_lon}"
                ET.SubElement(head, "second_position").text = f"{track_points[1]['lat']},{track_points[1]['lon']}"
                ET.SubElement(head, "end_position").text = f"{track_points[-1]['lat']},{track_points[-1]['lon']}"
                ET.SubElement(head, "points_num").text = str(len(track_points))
                ET.SubElement(head, "total_distance").text = str(int(distance * 100))
                ET.SubElement(head, "total_ascent").text = str(round(ascent))
                ET.SubElement(head, "grade").text = str(round(ascent*100+abs(descent)*100))

                
                lb = ET.SubElement(root, "leaderboard")
                ET.SubElement(lb, "leader_num").text = "1"
                li = ET.SubElement(lb, "leader_index", {"value": "1"})
                ET.SubElement(li, "name").text = "Leader"
                ET.SubElement(li, "memberID").text = "1234567"

                # Use leader_time_entry if there's a valid input in it, or use 1 second per point 
                try:
                    ET.SubElement(li, "time").text = str(int(self.leader_time_entry.get()))
                    use_leader_time = True
                except:
                    ET.SubElement(li, "time").text = str(len(track_points))
                    use_leader_time = False
                    
                ET.SubElement(li, "type").text = "5"

                ET.SubElement(root, "Encode").text = "2"
                ET.SubElement(root, "Tracks").text = ";".join(relative_points) + ";"
                ET.SubElement(root, "leader_time").text = self.compute_leader_times(int(self.leader_time_entry.get()),len(track_points)) if use_leader_time else ";".join("0" if t==0 else "1" for t in range(len(track_points))) + ";"
                ET.SubElement(root, "point_dist").text = ";".join(str(d) for d in point_dist_list) + ";"

                output_filename = os.path.join(output_dir, f"{random_id}_{trim_filename}_segment.cnx")
                xml_string = self.make_pretty_xml(root)
                with codecs.open(output_filename, "w", encoding='utf-8-sig') as f:
                    f.write('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n')
                    f.write(xml_string[xml_string.find('<segment'):])
                self.status_label.config(text="* DONE *")
            except Exception as e:
                self.status_label.config(text="* ERROR *")


# Run app
if __name__ == "__main__":
    root = tk.Tk()
    app = GPX2CNX(root)
    root.mainloop()
