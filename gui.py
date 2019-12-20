import os
import subprocess
import json
import webbrowser
from pymediainfo import MediaInfo
from threading import Thread
from appJar import gui
from constants import *

settings_file = "config.json"
if "_MEIPASS2" in os.environ:
    settings_file = os.path.join(os.environ["_MEIPASS2"], settings_file)
user_settings = json.load(open(settings_file))

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
    video_info = MediaInfo.parse(app.getEntry(FILE_PATH_ENTRY))

    multiplier = 1
    size = video_info.tracks[1].stream_size
    original_dur = int(video_info.tracks[1].mdhd_duration) / 1000
    changed_start = app.getEntry(START_FROM_ENTRY)
    changed_dur = app.getEntry(DURATION_ENTRY)
    if not changed_dur:
        if not changed_start:
            changed_dur = original_dur
        else:
            changed_dur = original_dur - int(changed_start)

    res = app.getOptionBox(RESOLUTION_OPTION_BOX)
    crf = app.getSpinBox(CRF_SPIN_BOX)
    preset = app.getOptionBox(PRESET_OPTION_BOX)
    preset_index = PRESET_OPTIONS.index(preset)

    if res == RES_720:
        multiplier *= 0.667

    multiplier *= (100 - float(crf) * (0.8 + (int(crf)/10))) / 67
    multiplier *= 20 / (preset_index + 20)
    multiplier *= float(changed_dur) / original_dur

    app.setLabel(SIZE_LABEL, SIZE_LABEL +
                 str(int(size / 1000 / 1000 * multiplier)) + " MB")


def trim_video_threaded():
    thread = Thread(target=trim_video)
    thread.start()


def trim_video():
    # get parameters
    selected_file = app.getEntry(FILE_PATH_ENTRY)

    start_from = app.getEntry(START_FROM_ENTRY)
    if not start_from:
        start_from = "0"

    duration = app.getEntry(DURATION_ENTRY)
    if not duration:
        duration = "0"

    resolution = app.getOptionBox(RESOLUTION_OPTION_BOX)
    crf = app.getSpinBox(CRF_SPIN_BOX)
    preset = app.getOptionBox(PRESET_OPTION_BOX)

    command = "ffmpeg -y " \
              "-ss " + start_from + \
              " -t " + duration + \
              " -i \"" + selected_file + \
              "\" -c:v libx264 -crf " + crf + \
              " -preset " + preset + \
              " -vf scale=" + resolution + \
              " \"" + file_path + "\""

    app.setMessage(LOG_MESSAGE, "Trimming started... \n\n")
    popen = subprocess.Popen(command, stdout=subprocess.PIPE, universal_newlines=True)
    exit_code = popen.wait()
    app.setMessage(LOG_MESSAGE, app.getMessage(LOG_MESSAGE) + "Trimming finished with exit code: " + str(exit_code))
    if exit_code:
        app.errorBox("Error", "There was an error while trimming...")


def open_options():
    app.showSubWindow(SETTINGS_TITLE)


def close_options():
    app.hideSubWindow(SETTINGS_TITLE)


def change_default_folder(button_name):
    path = app.directoryBox()

    if button_name == OUTPUT_CHANGE_BUTTON:
        user_settings["output_folder"] = path
        app.setEntry(OUTPUT_PATH_LABEL, path)
    elif button_name == INPUT_CHANGE_BUTTON:
        user_settings["input_folder"] = path
        app.setEntry(INPUT_PATH_LABEL, path)
    open_options()


def save_settings():
    if json.dump(user_settings, open(settings_file, "w")):
        close_options()


def open_ffmpeg_page():
    webbrowser.open("https://ffmpeg.zeranoe.com/builds/")


with gui(APP_TITLE, showIcon=False) as app:
    with app.labelFrame(PARAMETERS_FRAME):
        app.setIcon("resources/icons8-video-trimming-48.png")
        app.setSize(400, 600)
        app.setResizable(False)
        app.setTitle(APP_TITLE)

        # User Settings
        app.addMenuItem(SETTINGS_TITLE, SETTINGS_TITLE, open_options)
        app.addMenuList(HELP_TITLE, [FFMPEG_LINK], funcs=open_ffmpeg_page)
        app.startSubWindow(SETTINGS_TITLE)

        app.addLabel(OUTPUT_PATH_LABEL)
        app.addEntry(OUTPUT_PATH_LABEL, row="p", column=1)
        app.setEntry(OUTPUT_PATH_LABEL, user_settings["output_folder"])
        app.addButton(OUTPUT_CHANGE_BUTTON, change_default_folder, row="p", column=2)

        app.setSticky("we")
        app.addLabel(INPUT_PATH_LABEL)
        app.addEntry(INPUT_PATH_LABEL, row="p", column=1)
        app.setEntry(INPUT_PATH_LABEL, user_settings["input_folder"])
        app.addButton(INPUT_CHANGE_BUTTON, change_default_folder, row="p", column=2)

        app.setSticky("")
        app.addButton(SAVE_SETTINGS_BUTTON, save_settings, colspan=3)

        app.stopSubWindow()

        # Input File
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
        app.setSticky("ws")

        # Quality Settings
        app.addLabel(RESOLUTION_OPTION_BOX)
        app.addOptionBox(RESOLUTION_OPTION_BOX, SCALING_OPTIONS, row="p", column=1)
        app.setOptionBoxChangeFunction(RESOLUTION_OPTION_BOX, estimate_file_size)

        app.setSticky("w")
        app.addLabel(PRESET_OPTION_BOX)
        app.addOptionBox(PRESET_OPTION_BOX, PRESET_OPTIONS, row="p", column=1)
        app.setOptionBox(PRESET_OPTION_BOX, PRESET_OPTIONS.index("veryfast"))
        app.setOptionBoxChangeFunction(PRESET_OPTION_BOX, estimate_file_size)

        app.setSticky("wn")
        app.addLabel(CRF_SPIN_BOX)
        app.addSpinBox(CRF_SPIN_BOX, CRF_OPTIONS, row="p", column=1)
        app.setSpinBox(CRF_SPIN_BOX, 18)
        app.setSpinBoxWidth(CRF_SPIN_BOX, 3)
        app.setSpinBoxChangeFunction(CRF_SPIN_BOX, estimate_file_size)

        app.setStretch("both")
        app.setSticky("ws")

        # Trimming Settings
        app.addLabel(START_FROM_ENTRY)
        app.addEntry(START_FROM_ENTRY, row="p", column=1)
        app.setEntryWidth(START_FROM_ENTRY, 5)
        app.setEntryChangeFunction(START_FROM_ENTRY, estimate_file_size)

        app.setSticky("wn")
        app.addLabel(DURATION_ENTRY)
        app.addEntry(DURATION_ENTRY, row="p", column=1)
        app.setEntryWidth(DURATION_ENTRY, 5)
        app.setEntryChangeFunction(DURATION_ENTRY, estimate_file_size)

        app.setPadding([0, 10])
        app.setSticky("es")
        app.addNamedButton(SAVE_AS, OUTPUT_BUTTON, save_as)
        app.setSticky("s")
        app.addButton(TRIM_BUTTON, trim_video_threaded, row="p", column=1)
        app.setButtonBg(TRIM_BUTTON, "lightgreen")

        app.setExpand("NONE")
        app.setPadding([0, 0])
        app.setSticky("w")
        app.addLabel(SIZE_LABEL, colspan=3)
        app.setExpand("ALL")

    with app.labelFrame(LOG_FRAME):
        app.startScrollPane(LOG_FRAME)
        app.addEmptyMessage(LOG_MESSAGE)
        app.stopScrollPane()

app.go()
