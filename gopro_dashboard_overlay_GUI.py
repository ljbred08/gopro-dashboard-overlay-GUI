import FreeSimpleGUI as sg
import subprocess
import os
from collapsible_sections import CollapsibleSection
import collapsible_sections as cs
import sys
import shutil

# Set the output file suffix
OUTPUT_SUFFIX = "_dashboard"

size = (40, None)

section1_options = [
    {'label': 'Generate', 'key': 'generate', 'options': ['default', 'overlay', 'none'], 'default_value': 'default', 'tooltip': 'Type of output to generate. Overlay gives only the widgets with no video.'},
    {'label': 'Font', 'key': 'font', 'options': ['calibri', 'cambria', 'segoe ui', 'segoe print', 'liberation sans'], 'default_value': 'calibri'},
    {'label': 'Overlay Size', 'key': 'overlay_size', 'tooltip': '<XxY> e.g. 1920x1080 Force size of overlay. Use if video differs from supported bundled \noverlay sizes (1920x1080, 3840x2160), Required if --use-gpx-only (default: None).'},
    {'label': 'Background', 'key': 'bg', 'tooltip': 'Background Colour - R,G,B,A - each 0-255, no spaces! (default: (0, 0, 0, 0))', 'default_value': ''},
    {'label': 'Privacy', 'key': 'privacy', 'tooltip': 'Set privacy zone (lat,lon,km) (default: None)'},
    {'label': 'Config Dir', 'key': 'config_dir', 'tooltip': f'Location of config files (api keys, profiles, ...) (default: {os.path.join(os.path.expanduser("~"), ".gopro-graphics")})', 'default_value': ''},
    {'label': 'Cache Dir', 'key': 'cache_dir', 'tooltip': f'Location of caches (map tiles, ...) (default: {os.path.join(os.path.expanduser("~"), ".gopro-graphics")})', 'default_value': ''},
    {'label': 'FFMPEG DIR', 'key': 'ffmpeg_dir', 'tooltip': 'Directory where ffmpeg/ffprobe located, default=Look in PATH (default: None)', 'default_value': ''},
    {'label': 'GPX/FIT', 'key': 'gpx_fit', 'tooltip': 'Use GPX/FIT file for location / alt / hr / cadence / temp ... (default: None)', 'default_value': '', 'type': 'FileBrowse'},
    {'label': 'GPX Merge', 'key': 'gpx_merge', 'tooltip': '{EXTEND,OVERWRITE} When using GPX/FIT file - OVERWRITE=replace GPS/alt from GoPro with GPX values,\nEXTEND=just use additional values from GPX/FIT file e.g. hr/cad/power (default: MergeMode.EXTEND)', 'default_value': '', 'options': ['EXTEND', 'OVERWRITE']},
    {'label': 'Use GPX/FIT only', 'key': 'use_gpx_fit_only', 'tooltip': '--use-gpx-only, --use-fit-only\nUse only the GPX/FIT file - no GoPro location data (default: False)', 'default_value': '', 'options': ['', 'GPX', 'FIT']},
    {'label': 'Map API Key', 'key': 'map_api_key', 'tooltip': 'API Key for map provider, if required (default OSM doesn\'t need one) (default: None)', 'default_value': ''},
    {'label': 'Layout', 'key': 'layout', 'tooltip': '--layout {default,speed-awareness,xml}\nChoose graphics layout (default: default)', 'default_value': 'default', 'options': ['default', 'speed-awareness', 'xml']},
    {'label': 'Layout XML', 'key': 'layout_xml', 'tooltip': 'Use XML File for layout (default: None)', 'default_value': '', 'type': 'FileBrowse'},
    {'label': 'Exclude', 'key': 'exclude', 'tooltip': 'Exclude named component (will include all others) (default: None)', 'default_value': '', 'options': [
        'asi',
        'bar',
        'chart',
        'compass',
        'compass_arrow',
        'gps',
        'gradient_bar',
        'info',
        'map',
        'msi',
        'profile',
        'text',
    ]},
    {'label': 'Include', 'key': 'include', 'tooltip': '--include INCLUDE [INCLUDE ...]\nInclude named component (will exclude all others) (default: None)', 'default_value': '', 'options': [
        'asi',
        'bar',
        'chart',
        'compass',
        'compass_arrow',
        'gps',
        'gradient_bar',
        'info',
        'map',
        'msi',
        'profile',
        'text',
    ]},
    {'label': 'Units Speed', 'key': 'units_speed', 'tooltip': '--units-speed UNITS_SPEED\nDefault unit for speed. Many units supported: mph, mps, kph, knot, ... (default: mph)', 'default_value': 'mph', 'options': ['mph', 'mps', 'kph', 'knot', 'foot/second', 'metre/second', 'kilometre/hour', 'yard/second', 'inch/second', 'furlong/fortnight']},
    {'label': 'Units Altitude', 'key': 'units_altitude', 'tooltip': '--units-altitude UNITS_ALTITUDE\nDefault unit for altitude. Many units supported: foot, mile, metre, meter, parsec, angstrom, ... (default: foot)', 'default_value': 'foot', 'options': ['foot', 'mile', 'metre', 'meter', 'parsec', 'angstrom', 'astronomical unit', 'light year', 'nautical mile']},
    {'label': 'Units Distance', 'key': 'units_distance', 'tooltip': '--units-distance UNITS_DISTANCE\nDefault unit for distance. Many units supported: mile, km, foot, nmi, meter, metre, parsec, ... (default: mile)', 'default_value': 'mile', 'options': ['mile', 'km', 'foot', 'nmi', 'meter', 'metre', 'parsec']},
    {'label': 'Units Temperature', 'key': 'units_temperature', 'tooltip': '--units-temperature {kelvin,degC,degF}\nDefault unit for temperature (default: degF)', 'default_value': 'degF', 'options': ['kelvin', 'degC', 'degF']},
    {'label': 'GPS Speed Max', 'key': 'gps_speed_max', 'tooltip': '--gps-speed-max GPS_SPEED_MAX\nMax GPS Speed - Points with greater speed will be considered \'Not Locked\' (default: 60)', 'default_value': '60', 'options': []},

]

section1_layout = [
    [
        sg.Text(option['label'], tooltip=option.get('tooltip')),
        sg.Push(),
        {
            'Text': lambda: sg.InputText(key=option['key'], default_text=option.get('default_value'), size=size, tooltip=option.get('tooltip')),
            'Combo': lambda: sg.Combo(option.get('options', []), key=option['key'], default_value=option.get('default_value'), size=size, tooltip=option.get('tooltip')),
            'FileBrowse': lambda: sg.Input(key=option['key'], enable_events=True, size=size),
        }.get(option.get('type'), lambda: sg.Text(f'Unknown type: {option.get("type")}'))()
        if option.get('type')
        else (
            sg.Combo(option.get('options', []), key=option['key'], default_value=option.get('default_value'), size=size, tooltip=option.get('tooltip'))
            if option.get('options')
            else sg.InputText(key=option['key'], default_text=option.get('default_value'), size=size, tooltip=option.get('tooltip'))
        )
    ] + ([sg.FileBrowse(file_types=(('MP4 Files', '*.mp4'),))] if option.get('type') == 'FileBrowse' else [])
    for option in section1_options
]
section1 = CollapsibleSection(section1_layout, 'Advanced', '-SEC1-')


# Define the layout
layout = [
    [sg.Text('Input Video File  \u2009'), sg.Input(key='input_video', enable_events=True, size=size), sg.FileBrowse(file_types=(('Video Files', '*.mp4 *.avi *.mov *.wmv *.flv *.mkv *.m4v'),))],
    [sg.Text('Suffix                 '), sg.InputText(key='output_suffix', default_text=OUTPUT_SUFFIX, enable_events=True, size=size)],
    [sg.Text('Output Video File'), sg.Input(key='output_video',  size=size), sg.SaveAs(file_types=(('Video Files', '*.mp4 *.avi *.mov *.wmv *.flv *.mkv *.m4v'),))],
    [sg.Text('Map Style          '), sg.Combo([
        'local',
        'cyclosm',
        'geo-dark-matter-brown',
        'geo-dark-matter-dark-grey',
        'geo-dark-matter-dark-purple',
        'geo-dark-matter-purple-roads',
        'geo-dark-matter-yellow-roads',
        'geo-dark-matter',
        'geo-klokantech-basic',
        'geo-maptiler-3d',
        'geo-osm-bright-grey',
        'geo-osm-bright-smooth',
        'geo-osm-bright',
        'geo-osm-carto',
        'geo-osm-liberty',
        'geo-positron-blue',
        'geo-positron-red',
        'geo-positron',
        'geo-toner-grey',
        'geo-toner',
        'osm',
        'tf-atlas',
        'tf-cycle',
        'tf-landscape',
        'tf-mobile-atlas',
        'tf-neighbourhood',
        'tf-outdoors',
        'tf-pioneer',
        'tf-spinal-map',
        'tf-transport-dark',
        'tf-transport'
    ], key='map_style', default_value='local', size=size)],
    [section1.get_layout()],
    [sg.Button('Process'), sg.Button('Exit',tooltip='Exit the application. If command is running, it will be stopped instead of closing the window.')],
    [sg.Output(size=(80, 20), key='output_console')]
]

# Create the window
window = sg.Window('GoPro Dashboard Overlay GUI', layout, resizable=True)

# Function to run a command and display output in real-time
def run_command(cmd, window):
    try:
        print(f"Running command: {' '.join(cmd)}\n")
        p = subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in p.stdout:
            print(line, end='')  # Print to the PySimpleGUI Output element
            # Non-blocking read of the window
            event, values = window.read(timeout=0, timeout_key='-TIMED_OUT-')
            if event == '-TIMED_OUT-':
                continue
            if event == sg.WINDOW_CLOSED or event == 'Exit':
                p.kill()
                print("Command interrupted by user.")
                return p.wait()

        returncode = p.wait()
        print(f"Command exited with return code {returncode}")
        return returncode
    except Exception as e:
        print(f"Error running command: {e}")
        return None

# Event loop
while True:
    event, values = window.read()
    if event == sg.WINDOW_CLOSED or event == 'Exit':
        break
    
    try:
        cs.handle_section_events(window, event, section1)
    except Exception as e:
        print(f"Error handling section events: {e}")

    if event == 'input_video' or event == 'output_suffix':
        OUTPUT_SUFFIX = values['output_suffix']
        try:
            input_file_path = values['input_video']
            file_name, file_extension = os.path.splitext(input_file_path)
            output_file_path = f"{file_name}{OUTPUT_SUFFIX}{file_extension}"
            window['output_video'].update(output_file_path)
        except Exception as e:
            pass

    if event == 'Process':
        input_video = values['input_video']
        output_video = values['output_video']
        map_style = values['map_style']
        font = values['font'].lower()

        # Construct the command
        cmd = [sys.executable,shutil.which('gopro-dashboard.py'), f"{input_video}", f"{output_video}"]

        for key, value in values.items():
            if key not in ['input_video', 'output_video', 'output_suffix', 'Browse'] and value:
                cmd.extend([f"--{key.replace('_', '-')}",value])

        # Execute the command and display output in the terminal
        run_command(cmd, window)

window.close()
