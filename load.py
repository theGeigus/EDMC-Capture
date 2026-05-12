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


### Setup ###

__version__ = "0.1.0-beta"
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
image_type: Optional[tk.StringVar] = None
steam_move: Optional[tk.BooleanVar] = None
steam_path: Optional[tk.StringVar] = None

def plugin_start3(plugin_dir: str) -> str:
    logger.info(f"Starting {plugin_name} - Version {__version__}")
    
    global elite_path, image_move, image_path, image_type, steam_path, steam_move
    elite_path = tk.StringVar(value=config.get_str("capture_elite")) or ""
    image_move = tk.BooleanVar(value=config.get_bool("capture_move")) or 0
    image_path = tk.StringVar(value=config.get_str("capture_path")) or ""
    image_type = tk.StringVar(value=config.get_str("capture_type")) or ".png"
    steam_move = tk.BooleanVar(value=config.get_bool("capture_smove")) or 0
    steam_path = tk.StringVar(value=config.get_str("capture_spath")) or ""
    
    return plugin_name


### Config ###

def plugin_prefs(parent: nb.Notebook, cmdr: str, is_beta: bool) -> Optional[tk.Frame]:
    logger.debug("Loading Capture Settings")

    global elite_path, image_move, image_path, image_type, steam_path, steam_move
    
    extensions = [".png", ".jpg", ".bmp"]
    
    def update_ui_states(*args):
        i_entry.configure(state="normal" if image_move.get() else "disabled")
        s_entry.configure(state="normal" if steam_move.get() else "disabled")
        
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
    nb.Label(frame, text="File type:").grid(sticky=tk.W, row=3, column=0, padx=padx+10, pady=pady)
    combo = ttk.Combobox(frame, values=extensions, textvariable=image_type, state="readonly")
    combo.grid(sticky=tk.W, row=3, column=1, padx=padx, pady=pady)
    combo.set(image_type.get())
    
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
    ttk.Button(frame, text="Browse", command=browse_image_path).grid(sticky=tk.E, row=10, column=1, padx=padx, pady=pady)
    
    ttk.Separator(frame, orient=tk.HORIZONTAL).grid(row=11, column=0, columnspan=2, sticky=tk.EW, padx=padx, pady=pady)
    
    ### Steam Image
    nb.Label(frame, text="Add image to Steam screenshots (added after Steam restarts):").grid(sticky=tk.W, row=12, column=0, columnspan=2, padx=padx, pady=pady)
    
    nb.Checkbutton(frame, text="Add to Steam", variable=steam_move, command=update_ui_states).grid(sticky=tk.W, row=13, column=0, padx=padx+10, pady=pady)
    
    nb.Label(frame, text="Steam screenshot directory:").grid(sticky=tk.W, row=14, column=0, padx=padx+10, pady=pady)
    s_entry = ttk.Entry(frame, textvariable=steam_path)
    s_entry.grid(row=15, column=1, sticky=tk.EW, padx=padx, pady=pady)
    ttk.Button(frame, text="Browse", command=browse_steam_path).grid(sticky=tk.E, row=16, column=1, padx=padx, pady=pady)

    update_ui_states()

    return frame

def prefs_changed(cmdr: str, is_beta: bool) -> None:
    config.set("capture_elite", elite_path.get())
    config.set("capture_move", image_move.get())
    config.set("capture_path", image_path.get())
    config.set("capture_type", image_type.get())
    config.set("capture_smove", steam_move.get())
    config.set("capture_spath", steam_path.get())
    

## Events ###

def journal_entry(cmdr: str, is_beta: bool, system: str, station: str, entry: dict[str, Any], state: dict[str, Any]) -> str | None:
    if entry['event'] == 'Screenshot':
        
        ### DEBUG ###
        logger.info(f"Screenshot taken. Path: {entry["Filename"]}," + 
        f"Location: {state["SystemName"]}{f" - {state["Body"]}" if state["Body"] else f" - {state["Station"]}" if state["Station"] else ""}")
        # logger.debug(f"Interesting vars:\nCMDR:{cmdr}\n\nSystem:{system}\n\nStation:{station}\n\nEntry:{print_dict(entry)}\n\nState:{print_dict(state)}")
        ###

        filename = f"{state["SystemName"] or "Unknown"}{f" - {state["Body"]}" if state["Body"] else f" - {state["Station"]}" if state["Station"] else ""}"
        extension = image_type.get()

        original_path = Path(elite_path.get(), entry["Filename"].split("\\")[-1])
        
        logger.info(f"Found screenshot at {original_path}")
        
        ### Steam ###
        if steam_move.get():
            try: 
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                
                folder = Path(steam_path.get())
                
                counter = 1
                steam_save_path = folder / f"{timestamp}_1.jpg"
                
                while steam_save_path.exists():
                    counter += 1
                    target_path = folder / f"{timestamp}_{counter}.jpg"
            
                img = Image.open(original_path)
                img.save(steam_save_path)
                
                logger.info(f"Image saved to Steam: {steam_save_path}")
                
            except FileNotFoundError as e:
                logger.error(f"Could not find path \"{steam_save_path}\" - Is this path correct? Does EDMC have permission to access it?\n{e}")
            except Exception as e:
                logger.error(f"An unknown error has occurred: {e}")
        
        ### Image Directory ###        
        folder = Path(image_path.get()) if image_move.get() else Path(elite_path.get())
        
        target_path = folder / f"{filename}{extension}"
            
        counter = 0
        while target_path.exists():
            # If {target}.png exists, try {target}(1).png, etc.
            counter += 1
            target_path = folder / f"{filename}({counter}){extension}"
        
        try:
            img = Image.open(original_path)
            img.save(target_path)
            logger.info(f"Image moved to target: {target_path}")
            original_path.unlink()
            
        except FileNotFoundError as e:
            logger.error(f"Could not find path \"{original_path}\" - Is this path correct? Does EDMC have permission to access it?\n{e}")
        except Exception as e:
            logger.error(f"An unknown error has occurred: {e}")
