import subprocess
from pathlib import Path
from appJar import gui
from constants import *

file_path = DEFAULT_OUTPUT


def choose_file():
    selected_file = app.openBox(dirName="D:/Movies/Recordings")
    app.setEntry(FILE_PATH_ENTRY, selected_file)
    estimate_file_size()


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

    global file_path
    if path:
        file_path = path


def estimate_file_size():
    selected_file = Path(app.getEntry(FILE_PATH_ENTRY))
    info = selected_file.stat()

    multiplier = 1
    res = app.getOptionBox(RESOLUTION_OPTION_BOX)
    crf = app.getSpinBox(CRF_SPIN_BOX)
    preset = app.getOptionBox(PRESET_OPTION_BOX)

    if res == RES_720:
        multiplier *= 0.667

    multiplier *= (100 - float(crf) * 3.25) / 100

    app.setLabel("Size(estimated): ", "Size(estimated): " + str(info.st_size / 1000 / 1000 * multiplier) + " MB")


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

    crf = app.getSpinBox(CRF_SPIN_BOX)

    preset = app.getOptionBox(PRESET_OPTION_BOX)

    print(selected_file)
    print(resolution)

    command = "ffmpeg -y " \
              "-ss " + start_from + \
              " -t " + cut_from + \
              " -i \"" + selected_file + \
              "\" -c:v libx264 -crf " + crf + \
              " -preset " + preset + \
              " -vf scale=" + resolution + \
              " \"" + file_path + "\""
    print(command)
    popen = subprocess.Popen(command, stdout=subprocess.PIPE, universal_newlines=True)

    for line in popen.stdout:
        app.setMessage(LOG_MESSAGE, line.decode())
    popen.stdout.close()

    exit_code = popen.wait()
    if exit_code:
        app.errorBox("Error", "There was an error while trimming...")


with gui(APP_TITLE) as app:
    with app.labelFrame(OPTIONS_FRAME):
        app.setSize(640, 480)
        app.setTitle(APP_TITLE)
        app.icon_path = "resources/icons8-color-48.png"

        app.setExpand("NONE")
        app.setStretch("")
        app.setInPadding([5, 5])
        app.setSticky("w")
        app.addLabel(FILE_PATH_ENTRY)
        app.setSticky("we")
        app.addEntry(FILE_PATH_ENTRY, row="p", column=1)
        app.setSticky("w")
        app.setPadding([5, 0])
        app.addButton(BROWSE_BUTTON, choose_file, row="p", column=3)
        app.setPadding([0, 0])

        app.setExpand("ALL")
        app.setStretch("none")
        app.setSticky("w")

        app.addLabel(RESOLUTION_OPTION_BOX)
        app.addOptionBox(RESOLUTION_OPTION_BOX, SCALING_OPTIONS, row="p", column=1)
        app.setOptionBoxChangeFunction(RESOLUTION_OPTION_BOX, estimate_file_size)

        app.addLabel(PRESET_OPTION_BOX)
        app.addOptionBox(PRESET_OPTION_BOX, PRESET_OPTIONS, row="p", column=1)
        app.setOptionBox(PRESET_OPTION_BOX, PRESET_OPTIONS.index("veryfast"))

        app.addLabel(CRF_SPIN_BOX)
        app.addSpinBox(CRF_SPIN_BOX, CRF_OPTIONS, row="p", column=1)
        app.setSpinBox(CRF_SPIN_BOX, 18)
        app.setSpinBoxWidth(CRF_SPIN_BOX, 3)
        app.setSpinBoxChangeFunction(CRF_SPIN_BOX, estimate_file_size)

        app.setStretch("both")
        app.setSticky("ws")

        app.addLabel(START_FROM_ENTRY)
        app.addEntry(START_FROM_ENTRY, row="p", column=1)
        app.setEntryWidth(START_FROM_ENTRY, 5)

        app.setSticky("wn")
        app.addLabel(CUT_FROM_END_ENTRY)
        app.addEntry(CUT_FROM_END_ENTRY, row="p", column=1)
        app.setEntryWidth(CUT_FROM_END_ENTRY, 5)

        app.setSticky("")
        app.addNamedButton(SAVE_AS, OUTPUT_BUTTON, save_as)
        app.addButton(TRIM_BUTTON, trim_video, row="p", column=1)
        app.setButtonBg(TRIM_BUTTON, "lightgreen")

        app.addLabel("Size(estimated): ", colspan=2)

    with app.labelFrame(LOG_FRAME, row="p", column=2):
        app.addEmptyMessage(LOG_MESSAGE)

app.go()
