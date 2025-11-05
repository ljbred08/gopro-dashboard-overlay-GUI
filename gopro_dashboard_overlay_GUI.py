import FreeSimpleGUI as sg
import subprocess
import os
from collapsible_sections import CollapsibleSection
import collapsible_sections as cs
import sys
import shutil
from fontfinder import FontFinder

def get_available_fonts():
    """
    Get available system fonts with prioritized fonts at the top
    """
    preferred_fonts = ['calibri', 'cambria', 'segoe ui', 'segoe print', 'liberation sans']

    try:
        ff = FontFinder()
        system_fonts = ff.all_installed_families()

        # Prioritize preferred fonts that are available
        prioritized_fonts = []
        for preferred in preferred_fonts:
            for font in system_fonts:
                if preferred.lower() in font.lower():
                    prioritized_fonts.append(font)
                    break

        # Add other available fonts
        other_fonts = sorted([f for f in system_fonts if f not in prioritized_fonts])

        return prioritized_fonts + other_fonts[:50]  # Limit to reasonable number

    except Exception as e:
        print(f"Warning: Could not detect system fonts: {e}")
        return preferred_fonts  # Fallback to preferred list

# Get available fonts
available_fonts = get_available_fonts()

# Set the output file suffix
OUTPUT_SUFFIX = "_dashboard"

size = (40, None)

# Main advanced options (visible when Advanced section is expanded)
main_advanced_options = [
    {'label': 'Font', 'key': 'font', 'options': available_fonts, 'default_value': available_fonts[0] if available_fonts else 'calibri'},
    {'label': 'GPX/FIT', 'key': 'gpx_fit', 'tooltip': 'Use GPX/FIT file for location / alt / hr / cadence / temp ... (default: None)', 'default_value': '', 'type': 'FileBrowse'},
    {'label': 'Privacy', 'key': 'privacy', 'tooltip': 'Set privacy zone (lat,lon,km) (default: None)'},
    {'label': 'Layout', 'key': 'layout', 'tooltip': '--layout {default,speed-awareness,xml}\nChoose graphics layout (default: default)', 'default_value': 'default', 'options': ['default', 'speed-awareness', 'xml']},
    {'label': 'Layout XML', 'key': 'layout_xml', 'tooltip': 'Use XML File for layout (default: None)', 'default_value': '', 'type': 'FileBrowse'},
    {'label': 'Map API Key', 'key': 'map_api_key', 'tooltip': 'API Key for map provider, if required (default OSM doesn\'t need one) (default: None)', 'default_value': ''},
    {'label': 'Generate', 'key': 'generate', 'options': ['default', 'overlay', 'none'], 'default_value': 'default', 'tooltip': 'Type of output to generate. Overlay gives only the widgets with no video.'},
    {'label': 'Background', 'key': 'bg', 'tooltip': 'Background Colour - R,G,B,A - each 0-255, no spaces! (default: (0, 0, 0, 0))', 'default_value': ''},
    {'label': 'Overlay Size', 'key': 'overlay_size', 'tooltip': '<XxY> e.g. 1920x1080 Force size of overlay. Use if video differs from supported bundled \noverlay sizes (1920x1080, 3840x2160), Required if --use-gpx-only (default: None).'},
    {'label': 'Config Dir', 'key': 'config_dir', 'tooltip': f'Location of config files (api keys, profiles, ...) (default: {os.path.join(os.path.expanduser("~"), ".gopro-graphics")})', 'default_value': ''},
    {'label': 'Cache Dir', 'key': 'cache_dir', 'tooltip': f'Location of caches (map tiles, ...) (default: {os.path.join(os.path.expanduser("~"), ".gopro-graphics")})', 'default_value': ''},
]

# Nested collapsible sections
gpx_fit_options = [
    {'label': 'GPX Merge', 'key': 'gpx_merge', 'tooltip': '{EXTEND,OVERWRITE} When using GPX/FIT file - OVERWRITE=replace GPS/alt from GoPro with GPX values,\nEXTEND=just use additional values from GPX/FIT file e.g. hr/cad/power (default: MergeMode.EXTEND)', 'default_value': 'EXTEND', 'options': ['EXTEND', 'OVERWRITE']},
    {'label': 'Use GPX Only', 'key': 'use_gpx_only', 'tooltip': 'Use only the GPX file - no GoPro location data (default: False)', 'default_value': False},
    {'label': 'Use FIT Only', 'key': 'use_fit_only', 'tooltip': 'Use only the FIT file - no GoPro location data (default: False)', 'default_value': False},
    {'label': 'Video Time Start', 'key': 'video_time_start', 'tooltip': 'Use file dates for aligning video and GPS information, only when --use-gpx-only - EXPERIMENTAL!', 'default_value': '', 'options': ['file-created', 'file-modified', 'file-accessed']},
    {'label': 'Video Time End', 'key': 'video_time_end', 'tooltip': 'Use file dates for aligning video and GPS information, only when --use-gpx-only - EXPERIMENTAL!', 'default_value': '', 'options': ['file-created', 'file-modified', 'file-accessed']},
]

units_options = [
    {'label': 'Units Speed', 'key': 'units_speed', 'tooltip': '--units-speed UNITS_SPEED\nDefault unit for speed. Many units supported: mph, mps, kph, knot, ... (default: mph)', 'default_value': 'mph', 'options': ['mph', 'mps', 'kph', 'knot', 'foot/second', 'metre/second', 'kilometre/hour']},
    {'label': 'Units Altitude', 'key': 'units_altitude', 'tooltip': '--units-altitude UNITS_ALTITUDE\nDefault unit for altitude. Many units supported: foot, mile, metre, meter, parsec, angstrom, ... (default: metre)', 'default_value': 'metre', 'options': ['foot', 'mile', 'metre', 'meter', 'kilometre', 'nautical mile']},
    {'label': 'Units Distance', 'key': 'units_distance', 'tooltip': '--units-distance UNITS_DISTANCE\nDefault unit for distance. Many units supported: mile, km, foot, nmi, meter, metre, parsec, ... (default: mile)', 'default_value': 'mile', 'options': ['mile', 'km', 'foot', 'nmi', 'meter', 'metre', 'kilometre']},
    {'label': 'Units Temperature', 'key': 'units_temperature', 'tooltip': '--units-temperature {kelvin,degC,degF}\nDefault unit for temperature (default: degC)', 'default_value': 'degC', 'options': ['kelvin', 'degC', 'degF']},
]

render_options = [
    {'label': 'Profile', 'key': 'profile', 'tooltip': 'Use ffmpeg options profile from ffmpeg-profiles.json (default: None)', 'default_value': ''},
    {'label': 'Double Buffer', 'key': 'double_buffer', 'tooltip': 'Enable HIGHLY EXPERIMENTAL double buffering mode. May speed things up (default: False)', 'default_value': False},
    {'label': 'FFMPEG DIR', 'key': 'ffmpeg_dir', 'tooltip': 'Directory where ffmpeg/ffprobe located, default=Look in PATH (default: None)', 'default_value': ''},
]

gps_control_options = [
    {'label': 'GPS DOP Max', 'key': 'gps_dop_max', 'tooltip': 'Max DOP - Points with greater DOP will be considered \'Not Locked\' (default: 10)', 'default_value': '10'},
    {'label': 'GPS Speed Max', 'key': 'gps_speed_max', 'tooltip': 'Max GPS Speed - Points with greater speed will be considered \'Not Locked\' (default: 60)', 'default_value': '60'},
    {'label': 'GPS Speed Max Units', 'key': 'gps_speed_max_units', 'tooltip': 'Units for --gps-speed-max (default: kph)', 'default_value': 'kph', 'options': ['kph', 'mph', 'mps', 'knot']},
    {'label': 'GPS Bbox Lon Lat', 'key': 'gps_bbox_lon_lat', 'tooltip': 'Define GPS Bounding Box, anything outside will be considered \'Not Locked\' - minlon,minlat,maxlon,maxlat (default: None)', 'default_value': ''},
]

component_control_options = [
    {'label': 'Include', 'key': 'include', 'tooltip': '--include INCLUDE [INCLUDE ...]\nInclude named component (will exclude all others) (default: None)', 'default_value': '', 'options': [
        'asi', 'bar', 'chart', 'compass', 'compass_arrow', 'gps', 'gradient_bar', 'info', 'map', 'msi', 'profile', 'text',
    ]},
    {'label': 'Exclude', 'key': 'exclude', 'tooltip': 'Exclude named component (will include all others) (default: None)', 'default_value': '', 'options': [
        'asi', 'bar', 'chart', 'compass', 'compass_arrow', 'gps', 'gradient_bar', 'info', 'map', 'msi', 'profile', 'text',
    ]},
]

loading_options = [
    {'label': 'Load ACCL', 'key': 'load_accl', 'tooltip': 'Load accelerometer data (default: False)', 'default_value': False},
    {'label': 'Load GRAV', 'key': 'load_grav', 'tooltip': 'Load gravity data (default: False)', 'default_value': False},
    {'label': 'Load CORI', 'key': 'load_cori', 'tooltip': 'Load rotation sensor data (default: False)', 'default_value': False},
]

debug_options = [
    {'label': 'Show FFMPEG', 'key': 'show_ffmpeg', 'tooltip': 'Show FFMPEG output (not usually useful) (default: False)', 'default_value': False},
    {'label': 'Print Timings', 'key': 'print_timings', 'tooltip': 'Print timings (default: False)', 'default_value': False},
    {'label': 'Debug Metadata', 'key': 'debug_metadata', 'tooltip': 'Show detailed information when parsing GoPro Metadata (default: False)', 'default_value': False},
    {'label': 'Profiler', 'key': 'profiler', 'tooltip': 'Do some basic profiling of the widgets to find ones that may be slow (default: False)', 'default_value': False},
]

def create_option_layout(options):
    """Create layout for a list of options"""
    layout = []
    for option in options:
        # Handle boolean (checkbox) options
        if isinstance(option.get('default_value'), bool):
            layout.append([
                sg.Text(option['label'], tooltip=option.get('tooltip')),
                sg.Push(),
                sg.Checkbox('', key=option['key'], default=option.get('default_value', False), tooltip=option.get('tooltip'))
            ])
        # Handle FileBrowse options
        elif option.get('type') == 'FileBrowse':
            layout.append([
                sg.Text(option['label'], tooltip=option.get('tooltip')),
                sg.Push(),
                sg.Input(key=option['key'], enable_events=True, size=size, default_text=option.get('default_value', ''), tooltip=option.get('tooltip')),
                sg.FileBrowse(file_types=(('All Files', '*.*'),))
            ])
        # Handle options with dropdown list
        elif option.get('options'):
            layout.append([
                sg.Text(option['label'], tooltip=option.get('tooltip')),
                sg.Push(),
                sg.Combo(option.get('options', []), key=option['key'], default_value=option.get('default_value'), size=size, tooltip=option.get('tooltip'))
            ])
        # Handle regular text input
        else:
            layout.append([
                sg.Text(option['label'], tooltip=option.get('tooltip')),
                sg.Push(),
                sg.InputText(key=option['key'], default_text=option.get('default_value', ''), size=size, tooltip=option.get('tooltip'))
            ])
    return layout

# Create nested collapsible sections
gpx_fit_section = CollapsibleSection(create_option_layout(gpx_fit_options), 'GPX/FIT Options', '-GPX-')
units_section = CollapsibleSection(create_option_layout(units_options), 'Units Options', '-UNITS-')
render_section = CollapsibleSection(create_option_layout(render_options), 'Render Options', '-RENDER-')
gps_control_section = CollapsibleSection(create_option_layout(gps_control_options), 'GPS Control', '-GPS-')
component_control_section = CollapsibleSection(create_option_layout(component_control_options), 'Component Control', '-COMP-')
loading_section = CollapsibleSection(create_option_layout(loading_options), 'Loading Options', '-LOAD-')
debug_section = CollapsibleSection(create_option_layout(debug_options), 'Debug Options', '-DEBUG-')

# Create the main advanced layout with nested sections
advanced_layout = []

# Add main advanced options
advanced_layout.extend(create_option_layout(main_advanced_options))

# Add GPX/FIT options directly below GPX/FIT file input
gpx_file_row_index = None
for i, row in enumerate(advanced_layout):
    if any('GPX/FIT' in str(element) for element in row):
        gpx_file_row_index = i
        break

if gpx_file_row_index is not None:
    # Insert GPX/FIT section after the GPX/FIT file input
    gpx_layout = gpx_fit_section.get_layout()
    advanced_layout.insert(gpx_file_row_index + 1, gpx_layout[0])  # Header row
    advanced_layout.insert(gpx_file_row_index + 2, gpx_layout[1])  # Content row

# Add remaining nested sections - flatten the nested section layouts
for section in [units_section, render_section, gps_control_section, component_control_section, loading_section, debug_section]:
    section_layout = section.get_layout()
    advanced_layout.extend(section_layout)

# Create the main advanced section
section1 = CollapsibleSection(advanced_layout, 'Advanced', '-ADVANCED-')

# Create list of all collapsible sections for event handling
all_collapsible_sections = [
    section1,
    gpx_fit_section,
    units_section,
    render_section,
    gps_control_section,
    component_control_section,
    loading_section,
    debug_section,
]



# Define the layout
layout = [
    [sg.Text('Input Video File  \u2009'), sg.Input(key='input_video', enable_events=True, size=size), sg.FileBrowse(file_types=(('Video Files', '*.mp4 *.avi *.mov *.wmv *.flv *.mkv *.m4v'),))],
    [sg.Text('Suffix                 '), sg.InputText(key='output_suffix', default_text=OUTPUT_SUFFIX, enable_events=True, size=size)],
    [sg.Text('Output Video File'), sg.Input(key='output_video',  size=size), sg.SaveAs(file_types=(('Video Files', '*.mp4 *.avi *.mov *.wmv *.flv *.mkv *.m4v'),))],
    [sg.Text('Map Style          '), sg.Combo([
        'osm',
        'tf-cycle',
        'tf-transport',
        'tf-landscape',
        'tf-outdoors',
        'tf-transport-dark',
        'tf-spinal-map',
        'tf-pioneer',
        'tf-mobile-atlas',
        'tf-neighbourhood',
        'tf-atlas',
        'geo-osm-carto',
        'geo-osm-bright',
        'geo-osm-bright-grey',
        'geo-osm-bright-smooth',
        'geo-klokantech-basic',
        'geo-osm-liberty',
        'geo-maptiler-3d',
        'geo-toner',
        'geo-toner-grey',
        'geo-positron',
        'geo-positron-blue',
        'geo-positron-red',
        'geo-dark-matter',
        'geo-dark-matter-brown',
        'geo-dark-matter-dark-grey',
        'geo-dark-matter-dark-purple',
        'geo-dark-matter-purple-roads',
        'geo-dark-matter-yellow-roads',
        'local'
    ], key='map_style', default_value='osm', size=size)],
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
        cs.handle_sections_events(window, event, all_collapsible_sections)
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

        # Handle load options (can be combined)
        load_options = []
        for key in ['load_accl', 'load_grav', 'load_cori']:
            if values.get(key):
                if 'load_accl' == key:
                    load_options.append('ACCL')
                elif 'load_grav' == key:
                    load_options.append('GRAV')
                elif 'load_cori' == key:
                    load_options.append('CORI')
        if load_options:
            cmd.extend(['--load'] + load_options)

        for key, value in values.items():
            if key not in ['input_video', 'output_video', 'output_suffix', 'Browse', 'load_accl', 'load_grav', 'load_cori'] and value:
                # Special handling for GPX/FIT parameters
                if key == 'gpx_fit':
                    if value.lower().endswith('.gpx'):
                        cmd.extend(['--gpx', value])
                    elif value.lower().endswith('.fit'):
                        cmd.extend(['--fit', value])
                elif key == 'use_gpx_only':
                    if value:  # Boolean True
                        cmd.append('--use-gpx-only')
                elif key == 'use_fit_only':
                    if value:  # Boolean True
                        cmd.append('--use-fit-only')
                elif key == 'double_buffer':
                    if value:  # Boolean True
                        cmd.append('--double-buffer')
                elif key == 'show_ffmpeg':
                    if value:  # Boolean True
                        cmd.append('--show-ffmpeg')
                elif key == 'print_timings':
                    if value:  # Boolean True
                        cmd.append('--print-timings')
                elif key == 'debug_metadata':
                    if value:  # Boolean True
                        cmd.append('--debug-metadata')
                elif key == 'profiler':
                    if value:  # Boolean True
                        cmd.append('--profiler')
                else:
                    cmd.extend([f"--{key.replace('_', '-')}",value])

        # Execute the command and display output in the terminal
        run_command(cmd, window)

window.close()
