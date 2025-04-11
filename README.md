# GPXtoCNXConverter

This is a Python app for converting .GPX files to .CNX files. It allows you to export your tracks and waypoints (POI's). It also supports bulk conversion of multiple .GPX files. The app includes a tool for editing POI types, allowing appropriate icons to be used for POI's on the bike computer.

* CNX is a GIS data file format used by iGPSPORT GPS sport devices.
* GPX is an XML based format for GPS tracks.

## Data

The GPX2CNX tool in the app exports the following GPX data to the CNX file:

Track name from GPX tags.
    
Trackpoints:
* Latitude
* Longitude
* Elevation
    
Waypoints (POI's):
* Latitude
* Longitude
* Name

The app also calculates the following data based on the coordinates (features of the format and devices where it is used):
* Distance
* Ascent
* Descent
* Trackpoint count
* Waypoint count

The POI TYPES EDITOR tool in the app allows you to assign POI's to 23 supported icon types:
1. Waypoint
2. Sprint Point
3. HC Climb
4. Level 1 Climb
5. Level 2 Climb
6. Level 3 Climb
7. Level 4 Climb
8. Supply Point
9. Garbage recycle area
10. Restroom
11. Service Point
12. Medical Aid Station
13. Equipment Area
14. Shop
15. Meeting Point
16. Viewing Platform
17. Instagram-Worthy Location
18. Tunnel
19. Valley
10. Dangerous Road
21. Sharp Turn
22. Steep Slope
23. Intersection

## Run & Troubleshoot

This uses built-in Python libraries. To run on Python for Linux and older versions of Python for Windows, you may need to install tkinter module for Windows and python3-tk for Linux.

Nuitka is used to build the .exe file in the releases. Python applications packaged to .exe with various tools often trigger antivirus alerts. 

## Usage

Run the main.py script or gnx2cnx.exe (from the release) to start the GUI. Select the tool in the app for converting or changing POI types. 

#### GPX2CNX Tool

Browse and open your files. The converted files will be placed in the same directory as the original files, in a subfolder called 'cnx_routes'.

#### POI TYPES EDITOR Tool

Select the desired CNX file. All POI's from the track will be loaded with names and types. For each point, you can select the desired type from the dropdown menu. When you're done, click "Save All".


## Features

Converted files have names like 'route_original_file_name'. The part 'original_file_name' is truncated to 18 characters for better compatibility with bike computers.



