import PySimpleGUI as sg
import subprocess
import os

# Set the output file suffix
OUTPUT_SUFFIX = "_dashboard"

size = (40, None)

# Define the layout
layout = [
    [sg.Text('Input Video File  \u2009'), sg.Input(key='input_video', enable_events=True, size=size), sg.FileBrowse(file_types=(('MP4 Files', '*.mp4'),))],
    [sg.Text('Suffix                 '), sg.InputText(key='output_suffix', default_text=OUTPUT_SUFFIX, enable_events=True, size=size)],
    [sg.Text('Output Video File'), sg.Input(key='output_video',  size=size), sg.SaveAs(file_types=(('MP4 Files', '*.mp4'),))],
    [sg.Text('Font                  '), sg.Combo(['Calibri', 'Cambria', 'Segoe UI', 'Segoe Print', 'Liberation Sans'], key='font', default_value='Calibri', size=size)],  
    [sg.Text('Map Style          '), sg.Combo([
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
        'local',
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
    [sg.Button('Process'), sg.Button('Exit')],
    [sg.Output(size=(80, 20), key='output_console')]
]

# Create the window
window = sg.Window('GoPro Dashboard Overlay GUI', layout)

# Function to run a command and display output in real-time
def run_command(cmd, window):
    print(f"Running command: {' '.join(cmd)}\n")
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    for line in p.stdout:
        print(line, end='')  # Print to the PySimpleGUI Output element
    retval = p.wait()
    print(f"Command exited with return code {retval}")
    return retval

# Event loop
while True:
    event, values = window.read()
    if event == sg.WINDOW_CLOSED or event == 'Exit':
        break
    
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
        cmd = ['gopro-dashboard.py', f"{input_video}", f"{output_video}"]

        if map_style:
            cmd.extend(['--map-style', map_style])
        
        if font:
            cmd.extend(['--font', font])

        # Execute the command and display output in the terminal
        run_command(cmd, window)

window.close()
