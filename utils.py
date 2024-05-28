import tkinter as tk
from tkinter import filedialog

def get_max_speed(bandwidth_entry):
    try:
        return float(bandwidth_entry.get())
    except ValueError:
        return None

def prompt_save_location(url):
    default_filename = url.split("/")[-1]
    save_location = filedialog.asksaveasfilename(defaultextension=".part", initialfile=default_filename)
    return save_location
