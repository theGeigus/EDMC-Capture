from __future__ import annotations
import logging
import os

from config import appname, config
import edmc_data

import tkinter as tk
from tkinter import ttk, filedialog
from ttkHyperlinkLabel import HyperlinkLabel
import myNotebook as nb
from typing import Optional, Any

from EDMCLogging import get_main_logger
from PIL import Image
from pathlib import Path

from datetime import datetime

from threading import Thread, Lock
import re
from functools import partial


### Setup ###

__version__ = "0.1.0-beta.1"
plugin_name = os.path.basename(os.path.dirname(__file__))
plugin_url = "https://github.com/theGeigus/EDMC-Capture"
logger = logging.getLogger(f'{appname}.{plugin_name}')

if not logger.hasHandlers():
    level = logging.INFO

    logger.setLevel(level)
    logger_channel = logging.StreamHandler()
    logger_formatter = logging.Formatter(f'%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d:%(funcName)s: %(message)s')
    logger_formatter.default_time_format = '%Y-%m-%d %H:%M:%S'
    logger_formatter.default_msec_format = '%s.%03d'
    logger_channel.setFormatter(logger_formatter)
    logger.addHandler(logger_channel)

def print_dict(d: dict) -> str:
    res = ""
    for keys, values in d.items():
        res += f"    {keys}: {values}\n"
    return res

elite_path: Optional[tk.StringVar] = None
image_move: Optional[tk.BooleanVar] = None
image_path: Optional[tk.StringVar] = None
image_name: Optional[tk.StringVar] = None
image_type: Optional[tk.StringVar] = None
steam_move: Optional[tk.BooleanVar] = None
steam_path: Optional[tk.StringVar] = None

name_default = "{elite_year}-{month}-{day} {hour}_{minute}_{second} ({system} - {location})"

def from_template(txt, state):

    now = datetime.now()
    elite_year = now.year + 1286

    replacements = {
        "system": state.get("SystemName") or "Unknown System",
        "location": (state.get("Station") if state.get("Station") else state.get("Body")) or "Deep Space",
        "body": state.get("Body") or "Deep Space",
        "station": state.get("Station") or "Unknown",
        "ship": state.get("ShipName"),
        "ship_id": state.get("ShipIdent"),
        "month": now.strftime("%m"),
        "day": now.strftime("%d"),
        "year": now.strftime("%Y"),
        "elite_year": str(elite_year),
        "hour": now.strftime("%H"),
        "minute": now.strftime("%M"),
        "second": now.strftime("%S"),
    }

    return re.sub(r'[<>:"|?*]', '_', txt.format_map(replacements))

guide_instance = None

def guide_window(parent):

    global guide_instance

    if guide_instance is not None and guide_instance.winfo_exists():
        guide_instance.lift()
        guide_instance.focus_force()
        return

    guide_instance = tk.Toplevel(parent)
    guide_instance.title("Naming Guide")

    table = [
        "Naming Format:\n\n",
        "Files can be named using a template. The following keys can be used:\n\n",
        "|Variable       |Description                                                |Example        |\n",
        "|---------------|-----------------------------------------------------------|---------------|\n",
        "|`{system}`     |Current star system                                        |`Altair`       |\n",
        "|`{body}`       |Nearest planetary body (if any, otherwise \"Deep Space\")    |`Darkes Hollow`|\n",
        "|`{station}`    |Nearest station (if any, otherwise \"Unknown\")              |`Solo Orbiter` |\n",
        "|`{location}`   |Same as `{station}` if available, otherwise `{body}`       |`Solo Orbiter` |\n",
        "|`{ship}`       |The name of your current ship                              |`Teapot`       |\n",
        "|`{ship_id}`    |The ID of your current ship                                |`ER-418`       |\n",
        "|`{elite_year}` |In-game year                                               |`3312`         |\n",
        "|`{year}`       |Real-world year                                            |`2026`         |\n",
        "|`{month}`      |Month (01-12)                                              |`05`           |\n",
        "|`{day}`        |Day (01-31)                                                |`12`           |\n",
        "|`{hour}`       |Hour (00-23)                                               |`14`           |\n",
        "|`{minute}`     |Minute (00-59)                                             |`35`           |\n",
        "|`{second}`     |Second (00-59)                                             |`08`           |\n\n",
        "**Default template**: `{elite_year}-{month}-{day} {hour}_{minute}_{second} ({system} - {location})`\n\n",
        "**Note**: You can use `/` in your format to automatically sort screenshots into folders\n",
        "- Example: `{system}/{year}_{month}_{day}` will create a folder for the star system.\n",
    ]

    table_txt = "".join(table)

    txt = tk.Text(guide_instance, font=("Courier", 10), padx=10, pady=10, wrap=tk.NONE)
    txt.insert(tk.END, table_txt)
    txt.config(state="disabled")
    txt.pack(expand=True, fill="both")


def plugin_start3(plugin_dir: str) -> str:
    logger.info(f"Starting {plugin_name} - Version {__version__}")

    global elite_path, image_move, image_path, image_name, image_type, steam_move, steam_path
    elite_path = tk.StringVar(value=config.get_str("capture_elite") or "")
    image_move = tk.BooleanVar(value=config.get_bool("capture_move") or 0)
    image_path = tk.StringVar(value=config.get_str("capture_path") or "")
    image_name = tk.StringVar(value=config.get_str("capture_name") or name_default)
    image_type = tk.StringVar(value=config.get_str("capture_type") or ".png")
    steam_move = tk.BooleanVar(value=config.get_bool("capture_smove") or 0)
    steam_path = tk.StringVar(value=config.get_str("capture_spath") or "")

    return plugin_name


### Config ###

def plugin_prefs(parent: nb.Notebook, cmdr: str, is_beta: bool) -> Optional[tk.Frame]:
    logger.debug("Loading Capture Settings")

    global elite_path, image_move, image_path, image_type, steam_path, steam_move

    extensions = [".png", ".jpg", ".bmp"]

    sample_state = {
        "SystemName": "Altair",
        "Body": "Darkes Hollow",
        "Station": "Solo Orbiter",
        "ShipName": "Teapot",
        "ShipIdent": "ER-418"
    }

    def update_ui_states(*args):
        i_entry.configure(state="normal" if image_move.get() else "disabled")
        i_button.configure(state="normal" if image_move.get() else "disabled")
        s_entry.configure(state="normal" if steam_move.get() else "disabled")
        s_button.configure(state="normal" if steam_move.get() else "disabled")

    def update_preview(*args):
        preview_label.configure(text=f"Preview: {from_template(image_name.get(), sample_state)}{image_type.get()}")

    def browse_elite_path():
        directory = filedialog.askdirectory(initialdir=elite_path.get())
        if directory:
            elite_path.set(directory)

    def browse_image_path():
        directory = filedialog.askdirectory(initialdir=image_path.get())
        if directory:
            image_path.set(directory)

    def browse_steam_path():
        directory = filedialog.askdirectory(initialdir=steam_path.get())
        if directory:
            steam_path.set(directory)

    def check_path(path, error_text):
        if not path.exists():
            logger.error(f"Folder {folder} does not exist or EDMC does not have access to it. Check permissions and path.")
        else:
            return

    padx, pady = 5, 2

    frame = nb.Frame(parent)
    # frame.columnconfigure(0, minsize=200)
    frame.columnconfigure(1, weight=1)

    ### Label
    HyperlinkLabel(frame, text=plugin_name, url=plugin_url, underline=True).grid(sticky=tk.NW, row=0, column=0, padx=padx, pady=pady)
    nb.Label(frame, text=f"Version: {__version__}").grid(sticky=tk.NE, row=0, column=1, padx=padx, pady=pady)
    ttk.Separator(frame, orient=tk.HORIZONTAL).grid(row=1, column=0, columnspan=2, sticky=tk.EW, padx=padx, pady=pady)

    ### Image Type
    nb.Label(frame, text="Convert image").grid(sticky=tk.W, row=2, column=0, padx=padx, pady=pady)
    nb.Label(frame, text="File name:").grid(sticky=tk.W, row=3, column=0, padx=padx+10, pady=pady)

    file_frame = nb.Frame(frame)
    file_frame.columnconfigure(1, weight=1)
    file_frame.grid(sticky=tk.EW, row=3, column=1, padx=padx, pady=pady)

    file_field = ttk.Entry(file_frame, textvariable=image_name)
    file_field.grid(sticky=tk.EW, row=1, column=1)
    image_name.trace_add('write', update_preview)

    combo = ttk.Combobox(file_frame, values=extensions, textvariable=image_type, state="readonly")
    combo.grid(sticky=tk.EW, row=1, column=2)
    combo.set(image_type.get())
    image_type.trace_add('write', update_preview)

    preview_label = nb.Label(file_frame, text=f"Preview: {from_template(image_name.get(), sample_state)}{image_type.get()}")
    preview_label.grid(sticky=tk.EW, row=2, column=1)

    ttk.Button(file_frame, text="Guide", command=partial(guide_window, parent)).grid(sticky=tk.E, row=2, column=2, pady=pady)

    ### Elite Image
    nb.Label(frame, text="Elite image directory:").grid(sticky=tk.W, row=4, column=0, padx=padx+10, pady=pady)
    ttk.Entry(frame, textvariable=elite_path).grid(sticky=tk.EW, row=4, column=1, padx=padx, pady=pady)
    ttk.Button(frame, text="Browse", command=browse_elite_path).grid(sticky=tk.E, row=5, column=1, padx=padx, pady=pady)

    ttk.Separator(frame, orient=tk.HORIZONTAL).grid(row=6, column=0, columnspan=2, sticky=tk.EW, padx=padx, pady=pady)

    ### New Image
    nb.Label(frame, text="Move image to new location").grid(sticky=tk.W, row=7, column=0, padx=padx, pady=pady)

    nb.Checkbutton(frame, text="Move image", variable=image_move, command=update_ui_states).grid(sticky=tk.W, row=8, column=0, padx=padx+10, pady=pady)

    nb.Label(frame, text="Image directory:").grid(sticky=tk.W, row=9, column=0, padx=padx+10, pady=pady)
    i_entry = ttk.Entry(frame, textvariable=image_path)
    i_entry.grid(row=9, column=1, sticky=tk.EW, padx=padx, pady=pady)
    i_button = ttk.Button(frame, text="Browse", command=browse_image_path)
    i_button.grid(sticky=tk.E, row=10, column=1, padx=padx, pady=pady)


    ttk.Separator(frame, orient=tk.HORIZONTAL).grid(row=11, column=0, columnspan=2, sticky=tk.EW, padx=padx, pady=pady)

    ### Steam Image
    nb.Label(frame, text="Add image to Steam screenshots (added after Steam restarts):").grid(sticky=tk.W, row=12, column=0, columnspan=2, padx=padx, pady=pady)

    nb.Checkbutton(frame, text="Add to Steam", variable=steam_move, command=update_ui_states).grid(sticky=tk.W, row=13, column=0, padx=padx+10, pady=pady)

    nb.Label(frame, text="Steam screenshot directory:").grid(sticky=tk.W, row=14, column=0, padx=padx+10, pady=pady)
    s_entry = ttk.Entry(frame, textvariable=steam_path)
    s_entry.grid(row=15, column=1, sticky=tk.EW, padx=padx, pady=pady)
    s_button = ttk.Button(frame, text="Browse", command=browse_steam_path)
    s_button.grid(sticky=tk.E, row=16, column=1, padx=padx, pady=pady)

    update_ui_states()

    return frame

def prefs_changed(cmdr: str, is_beta: bool) -> None:
    config.set("capture_elite", elite_path.get())
    config.set("capture_move", image_move.get())
    config.set("capture_path", image_path.get())
    config.set("capture_name", image_name.get())
    config.set("capture_type", image_type.get())
    config.set("capture_smove", steam_move.get())
    config.set("capture_spath", steam_path.get())


## Events ###

steam_lock = Lock()
file_lock = Lock()

def handle_screenshot(filename, extension, original_path, move, move_dir, steam, steam_dir, elite_dir):
    ### Steam
    if steam:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

            folder = Path(steam_dir)

            steam_save_dir = folder / f"{timestamp}_1.jpg"

            with steam_lock:
                counter = 1
                while steam_save_dir.exists():
                    counter += 1
                    steam_save_dir = folder / f"{timestamp}_{counter}.jpg"
                try:
                    with Image.open(original_path) as img:
                        img.save(steam_save_dir)

                    logger.info(f"Image saved to Steam: {steam_save_dir}")

                except FileNotFoundError as e:
                    logger.error(f"Could not find path \"{steam_save_dir}\" - Is this path correct? Does EDMC have permission to access it?\n{e}")
                except Exception as e:
                    logger.error(f"An unknown error has occurred: {e}")

    ### Image Directory
    folder = Path(move_dir) if move else Path(elite_dir)

    if not folder.exists():
        logger.error(f"Folder {folder} does not exist or EDMC does not have access to it. Check permissions and path.")
        return

    target_path = folder / f"{filename}{extension}"
    target_path.parent.mkdir(parents=True, exist_ok=True)

    counter = 0

    with file_lock:
        while target_path.exists():
            # If {target}.png exists, try {target}(1).png, etc.
            counter += 1
            target_path = folder / f"{filename}({counter}){extension}"

        try:
            with Image.open(original_path) as img:
                img.save(target_path)
            logger.info(f"Image moved to target: {target_path}")
            original_path.unlink()

        except FileNotFoundError as e:
            logger.error(f"Could not find path \"{original_path}\" - Is this path correct? Does EDMC have permission to access it?\n{e}")
        except Exception as e:
            logger.error(f"An unknown error has occurred: {e}")

def journal_entry(cmdr: str, is_beta: bool, system: str, station: str, entry: dict[str, Any], state: dict[str, Any]) -> str | None:
    if entry['event'] == 'Screenshot':

        ### DEBUG ###
        logger.info(f"Screenshot taken. Path: {entry["Filename"]}," +
        f"Location: {state.get("SystemName")}{f" - {state.get("Body")}" if state.get("Body") else f" - {state.get("Station")}" if state.get("Station") else ""}")
        # logger.debug(f"Interesting vars:\nCMDR:{cmdr}\n\nSystem:{system}\n\nStation:{station}\n\nEntry:{print_dict(entry)}\n\nState:{print_dict(state)}")
        ###

        filename = from_template(image_name.get(), state)

        logger.info(f"Image name: {filename}")

        extension = image_type.get()

        original_path = Path(elite_path.get()) / Path(entry["Filename"].split("\\")[-1])

        logger.info(f"Found screenshot at {original_path}")

        Thread(target=handle_screenshot, args=(filename, extension, original_path, image_move.get(), image_path.get(), steam_move.get(), steam_path.get(), elite_path.get()), daemon=True).start()
