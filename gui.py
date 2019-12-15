import subprocess
from appJar import gui
from contants import *


def choose_file():
    selected_file = app.openBox(dirName="D:/Movies/Recordings")
    app.setEntry(FILE_PATH_ENTRY, selected_file)


def save_as():
    file_name = app.getButton(OUTPUT_BUTTON)
    file_types = [("videos", ".mp4")]

    if file_name == SAVE_AS:
        path = app.saveBox(fileTypes=file_types,
                           fileName="out",
                           dirName="D:/Movies/Recordings/Trimmed Recordings",
                           fileExt=file_types[0])
    else:
        path = app.saveBox(fileName=file_name,
                           fileTypes=file_types)

    if path:
        app.setButton(OUTPUT_BUTTON, path)
    else:
        app.setButton(OUTPUT_BUTTON, SAVE_AS)


def trim_video():
    # get parameters
    selected_file = app.getEntry(FILE_PATH_ENTRY)

    resolution = app.getOptionBox(RESOLUTION_OPTION_BOX)

    start_from = app.getEntry(START_FROM_ENTRY)
    if not start_from:
        start_from = "0"

    cut_from = app.getEntry(CUT_FROM_END_ENTRY)
    if not cut_from:
        cut_from = "0"

    crf = app.getOptionBox(CRF_OPTION_BOX)

    preset = app.getOptionBox(PRESET_OPTION_BOX)

    output_path = app.getButton(OUTPUT_BUTTON)
    if output_path == SAVE_AS:
        output_path = DEFAULT_OUTPUT

    print(selected_file)
    print(resolution)

    command = "ffmpeg -y " \
              "-ss " + start_from + \
              " -t  " + cut_from + \
              " -i \"" + selected_file + \
              "\" -c:v libx264 -crf " + crf + \
              " -preset " + preset + \
              "-vf scale=" + resolution + \
              " \"" + output_path + "\""
    print(command)
    subprocess.Popen(command, stdout=subprocess.PIPE)


with gui(APP_TITLE) as app:
    with app.labelFrame(OPTIONS_FRAME):
        app.setSize(640, 480)
        app.setTitle(APP_TITLE)

        app.addLabelEntry(FILE_PATH_ENTRY)
        app.setSticky("w")
        app.addButton(BROWSE_BUTTON, choose_file, row=0, column=1)
        app.addLabelOptionBox(RESOLUTION_OPTION_BOX, SCALING_OPTIONS)
        app.addLabelOptionBox(CRF_OPTION_BOX, CRF_OPTIONS)
        app.addLabelOptionBox(PRESET_OPTION_BOX, PRESET_OPTIONS)
        app.setOptionBox(PRESET_OPTION_BOX, PRESET_OPTIONS.index("veryslow"))
        app.addLabelEntry(START_FROM_ENTRY)
        app.setEntryDefault(START_FROM_ENTRY, TIME_PLACEHOLDER)
        app.addLabelEntry(CUT_FROM_END_ENTRY)
        app.setEntryDefault(CUT_FROM_END_ENTRY, TIME_PLACEHOLDER)
        app.setSticky("")
        app.addNamedButton(SAVE_AS, OUTPUT_BUTTON, save_as)
        app.setSticky("w")
        app.addButton(TRIM_BUTTON, trim_video, row=6, column=1)

    with app.labelFrame(LOG_FRAME, row=0, column=2):
        app.addEmptyMessage(LOG_MESSAGE)

app.go()
