# GPXtoCNXConverter

This is a Python script for converting .GPX files to .CNX files. It allows you to export your tracks and waypoints (POIs). The script supports bulk conversion of multiple .GPX files.

* CNX is a GIS data file format used by iGPSPORT GPS sport devices.
* GPX is an XML based format for GPS tracks.

## Data

The script exports the following GPX data to the CNX file:

Track name from GPX tags.
    
Trackpoints:
* Latitude
* Longitude
* Elevation
    
Waypoints (POIs):
* Latitude
* Longitude
* Name

The script also calculates the following data based on the coordinates (features of the format and devices where it is used):

* Distance
* Ascent
* Descent
* Trackpoint count
* Waypoint count

## Run & Troubleshoot

This uses built-in Python libraries. To run on Python for Linux and older versions of Python for Windows, you may need to install tkinter module for Windows and python3-tk for Linux.

## Usage

Run the gnx2cnx.py script or gnx2cnx.exe (from the release) to start the GUI. Browse and open your files. The converted files will be placed in the same directory as the original files, in a subfolder called 'cnx_routes'.

## Features

Converted files have names like 'route_original_file_name'. The part 'original_file_name' is truncated to 18 characters for better compatibility with bike computers.



