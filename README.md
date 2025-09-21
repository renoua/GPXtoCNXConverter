# Strava Segments to IGPSPORT

This is a Python app for converting Strava Segments .GPX files to .CNX IGPSPORT compatibles files.

* CNX is a GIS data file format used by iGPSPORT GPS sport devices.
* GPX is an XML based format for GPS tracks.

## Data

The GPX2CNX tool in the app exports the following GPX data to the CNX file:

## Run & Troubleshoot

This uses built-in Python libraries. To run on Python for Linux and older versions of Python for Windows, you may need to install tkinter module for Windows and python3-tk for Linux.

Nuitka is used to build the .exe file in the releases. Python applications packaged to .exe with various tools often trigger antivirus alerts. 

## Usage

Run the main.py script to start the GUI. Type in the KOM time and select the .GPX file. 

#### GPX2CNX Tool

Browse and open your files. The converted files will be placed in the same directory as the original files, in a subfolder called 'cnx_routes'.

## Features

Converted files have names like 'route_original_file_name'. The part 'original_file_name' is truncated to 18 characters for better compatibility with bike computers.



