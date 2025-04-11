# poi_types_editor.py
from pathlib import Path
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from xml.etree import ElementTree as ET
import codecs


ROOT_DIR = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT_DIR / 'config'
TYPES_LIST_FILE = 'poi_types_list.txt'
LIST_FILEPATH = CONFIG_PATH / TYPES_LIST_FILE


# Loads POI types from a file as a dictionary {code: name}
def load_poi_types(filepath=LIST_FILEPATH):
    poi_types = {}
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if line:
                    parts = line.split(',')
                    if len(parts) == 2:
                        type_code = parts[0].strip()
                        type_name = parts[1].strip()
                        poi_types[type_code] = type_name
    except FileNotFoundError:
        poi_types = {"0": "Waypoint"}  # default value
    return poi_types


class POIEditor:
    # Creating GUI and calling button functions
    def __init__(self, root):
        self.root = root
        root.title("POI TYPES EDITOR")

        self.poi_types = load_poi_types()
        self.type_list_for_combo = list(self.poi_types.values())
        self.points = []
        self.current_index = 0
        self.xml_filepath = None
        self.xml_tree = None
        self.xml_root = None

        self.name_label = tk.Label(root, text="POI Name:")
        self.name_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)

        self.name_text = tk.StringVar()
        self.name_entry = ttk.Entry(root, textvariable=self.name_text, state="readonly", width=50)
        self.name_entry.grid(row=0, column=1, columnspan=2, sticky="ew", padx=5, pady=5)

        self.type_label = ttk.Label(root, text="POI Type:")
        self.type_label.grid(row=1, column=0, sticky="w", padx=5, pady=5)

        self.type_combo = ttk.Combobox(root, values=self.type_list_for_combo, state="readonly")
        self.type_combo.grid(row=1, column=1,columnspan=3, sticky="ew", padx=5, pady=5)
        self.type_combo.bind("<<ComboboxSelected>>", self.update_current_poi_type)

        self.prev_button = ttk.Button(root, text="Prev", command=self.show_previous_poi, state="disabled")
        self.prev_button.grid(row=2, column=0, sticky="ew", padx=5, pady=10)

        self.next_button = ttk.Button(root, text="Next", command=self.show_next_poi, state="disabled")
        self.next_button.grid(row=2, column=1, sticky="ew", padx=5, pady=10)

        self.counter_label = ttk.Label(root, text="0/0")
        self.counter_label.grid(row=2, column=2, sticky="ew", padx=5, pady=10)

        self.save_button = ttk.Button(root, text="Save All", command=self.save_all_changes, state="disabled")
        self.save_button.grid(row=3, column=0, columnspan=3, sticky="ew", padx=5, pady=10)

        self.load_button = ttk.Button(root, text="Load CNX", command=self.load_cnx)
        self.load_button.grid(row=4, column=0, columnspan=3, sticky="ew", padx=5, pady=10)

        self.status_label = ttk.Label(root, text="")
        self.status_label.grid(row=5, column=0, columnspan=3, sticky="e", padx=5, pady=5)

        root.grid_columnconfigure(1, weight=1)

    # Loads file and parses the data
    def load_cnx(self):
        filepath = filedialog.askopenfilename(
            defaultextension=".cnx",
            filetypes=[("CNX files", "*.cnx")],
            title="Select CNX file"
        )
        if filepath:
            try:
                self.xml_tree = ET.parse(filepath)
                self.xml_root = self.xml_tree.getroot()
                points_element = self.xml_root.find("Points")
                if points_element is not None:
                    self.points = []
                    for point_element in points_element.findall("Point"):
                        lat = point_element.findtext("Lat")
                        lng = point_element.findtext("Lng")
                        type_val = point_element.findtext("Type")
                        descr = point_element.findtext("Descr")
                        self.points.append({"lat": lat, "lng": lng, "type": type_val, "descr": descr, "element": point_element})
                    if self.points:
                        self.current_index = 0
                        self.show_current_poi()
                        self.prev_button["state"] = "disabled"
                        self.next_button["state"] = "normal" if len(self.points) > 1 else "disabled"
                        self.save_button["state"] = "normal"
                        self.status_label.config(text=f"* Loaded {len(self.points)} POI's *")
                        self.xml_filepath = filepath
                    else:
                        self.status_label.config(text="* No POI's found in the file *")
                        self.clear_ui()
                        self.xml_filepath = None
                else:
                    self.status_label.config(text="* The <Points> element not found in the file *")
                    self.clear_ui()
                    xml_filepath = None
            except ET.ParseError:
                self.status_label.config(text="* CNX file parsing error *")
                self.clear_ui()
                self.xml_filepath = None
            except FileNotFoundError:
                self.status_label.config(text="* File not found *")
                self.clear_ui()
                self.xml_filepath = None

    # Displays the current POI in the interface
    def show_current_poi(self):
        if self.points:
            current_poi = self.points[self.current_index]
            self.name_text.set(current_poi["descr"])
            poi_type = self.poi_types.get(current_poi["type"], f"Unknown type ({current_poi['type']})")
            self.type_combo.set(poi_type)
            self.counter_label.config(text=f"{self.current_index + 1}/{len(self.points)}")

    # Next POI
    def show_next_poi(self):
        if self.current_index < len(self.points) - 1:
            self.current_index += 1
            self.show_current_poi()
            self.prev_button["state"] = "normal"
            if self.current_index == len(self.points) - 1:
                self.next_button["state"] = "disabled"

    # Prev POI
    def show_previous_poi(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.show_current_poi()
            self.next_button["state"] = "normal"
            if self.current_index == 0:
                self.prev_button["state"] = "disabled"

    # Returns the type code by type name
    def get_type_code(self, type_name):
        for code, name in self.poi_types.items():
            if name == type_name:
                return code
        return "0"  # default value

    # Updates the type of the current POI in the self.points list when a value is selected in the Combobox
    def update_current_poi_type(self, event):
        if self.points and 0 <= self.current_index < len(self.points):
            selected_type_name = self.type_combo.get()
            selected_type_code = self.get_type_code(selected_type_name)
            self.points[self.current_index]["type"] = selected_type_code

    # Saves all changes to the original file
    def save_all_changes(self):
        if self.points and self.xml_filepath and self.xml_tree:
            points_element = self.xml_root.find("Points")
            if points_element is not None:
                for i, poi in enumerate(self.points):
                    point_element = points_element[i]
                    point_element.find("Type").text = poi["type"]
                try:
                    xml_string = ET.tostring(self.xml_root, encoding='unicode')
                    with codecs.open(self.xml_filepath, "w", encoding='utf-8-sig') as f:
                        f.write('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n')
                        f.write(xml_string[xml_string.find('<Route'):])
                    self.status_label.config(text="* SAVED *")
                except Exception as e:
                    self.status_label.config(text=f"* File save error: {e} *")
            else:
                self.status_label.config(text="* Error: <Points> element not found for saving *")
        elif not self.xml_filepath:
            self.status_label.config(text="* CNX file not loaded *")
        elif not self.xml_tree:
            self.status_label.config(text="* Error working with the XML tree *")

    # Clearing UI elements
    def clear_ui(self):
        self.name_text.set("")
        self.type_combo.set("")
        self.prev_button["state"] = "disabled"
        self.next_button["state"] = "disabled"
        self.save_button["state"] = "disabled"


# Run app
if __name__ == "__main__":
    root = tk.Tk()
    app = POIEditor(root)
    root.mainloop()