# Strava Segments to IGPSPORT

This is a Python app for converting Strava Segments .GPX files to .CNX IGPSPORT compatible files.

* CNX is a GIS data file format used by iGPSPORT GPS sport devices.
* GPX is an XML based format for GPS tracks.

## Data

The app exports the following GPX data to the CNX file.

## Run & Troubleshoot

This uses built-in Python libraries. To run on Python for Linux and older versions of Python for Windows, you may need to install tkinter module for Windows and python3-tk for Linux.

## Usage

Run the main.py script to start the GUI. Type in the KOM time and select the .GPX file.
The converted files will be placed in the same directory as the original files, in a subfolder called 'cnx_routes'.

## Features

Converted files have names like 'randomid_original_file_name_segment' to make them suitable for IGPSPORT Segments. The part 'original_file_name' is truncated to 18 characters for better compatibility with bike computers.



