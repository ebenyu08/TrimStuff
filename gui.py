import subprocess
from appJar import gui
from contants import *


def choose_file():
    selected_file = app.openBox()
    app.setEntry(FILE_PATH_ENTRY, selected_file)


def save_as():
    file_name = app.getButton(OUTPUT_BUTTON)
    file_types = [("videos", ".mp4")]

    if file_name == SAVE_AS:
        path = app.saveBox(fileTypes=file_types)
    else:
        path = app.saveBox(fileName=file_name, fileTypes=file_types)

    if path:
        app.setButton(OUTPUT_BUTTON, path)
    else:
        app.setButton(OUTPUT_BUTTON, SAVE_AS)


def trim_video():
    selected_file = app.getEntry(FILE_PATH_ENTRY)
    resolution = app.getOptionBox(RESOLUTION_OPTION_BOX)
    start_from = app.getEntry(START_FROM_ENTRY)
    cut_from = app.getEntry(CUT_FROM_END_ENTRY)
    output_path = app.getButton(OUTPUT_BUTTON)
    print(selected_file)
    print(resolution)

    command = "ffmpeg -ss " + start_from + " -t  " + cut_from + " " \
              "-i \"" + selected_file + "\" " + \
              "-vf scale=" + resolution + " "\
              "\"" + output_path + "\""
    print(command)
    with subprocess.Popen(command, stdout=subprocess.PIPE) as process:
        for line in iter(process.stdout.readline()):
            app.setMessage(LOG_MESSAGE, line)


with gui(APP_TITLE) as app:

    with app.labelFrame(OPTIONS_FRAME):
        app.setSize(640, 480)
        app.addLabel(TITLE_LABEL, APP_TITLE)

        app.addLabelEntry(FILE_PATH_ENTRY)
        app.addButton(BROWSE_BUTTON, choose_file)
        app.addLabelOptionBox(RESOLUTION_OPTION_BOX, SCALING_OPTIONS)
        app.addLabelEntry(START_FROM_ENTRY)
        app.setEntryDefault(START_FROM_ENTRY, TIME_PLACEHOLDER)
        app.addLabelEntry(CUT_FROM_END_ENTRY)
        app.setEntryDefault(CUT_FROM_END_ENTRY, TIME_PLACEHOLDER)
        app.addNamedButton(SAVE_AS, OUTPUT_BUTTON, save_as)
        app.addButton(TRIM_BUTTON, trim_video)

    with app.labelFrame(LOG_FRAME, row=0, column=1):
        app.addEmptyMessage(LOG_MESSAGE)

app.go()
