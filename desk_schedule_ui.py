import hashlib
import os
import sys
import glob
import pathlib
import zipfile
from pathlib import Path
from ctypes.wintypes import MAX_PATH

from tkinter import filedialog, messagebox
from tkinter import Tk, Button, Label, font, StringVar, Checkbutton

from functools import partial
from unicodedata import normalize

from parse_absences import parse_absences
from errors import error_file, error_file_header, init_error_log, log_message, get_stack_trace

version = "1.0"

horaires = None
absences = None


def get_horaire_file():
    global horaires
    filetypes = (
        ('text files', '*.xlsx'),
        ('All files', '*.*')
    )
    d_title = "Choose the Horaires XLSX file"
    horaires = filedialog.askopenfilename(initialdir=Path.home(), filetypes=filetypes, title=d_title)


def get_absence_file():
    global absences
    filetypes = (
        ('text files', '*.html'),
        ('All files', '*.*')
    )
    d_title = "Choose the absences.epfl.ch file (saved HTML)"
    absences = filedialog.askopenfilename(initialdir=Path.home(), filetypes=filetypes, title=d_title)


def run_desk_schedule(tkroot, width_chars):
    global horaires
    global absences
    print(horaires)
    print(absences)    

    error_message = f"There were errors or warnings during processing:\ncheck {error_file} for information."

    init_error_log()
    
    if absences is not None:
        parse_absences(absences)

    if horaires is not None:
        # TODO call or-librarydesk-schedule, need to make it a module first
        pass


    f_err = open(error_file, "r")
    error_content = f_err.read()
    f_err.close()
    
    if error_content.replace('\r', '').replace('\n', '') == error_file_header.replace('\r', '').replace('\n', ''):
        os.remove(error_file)
    else:
        error_info = Label(tkroot, text=error_message)
        error_info.pack()

    done_info = Label(tkroot, text=f'Done: desk_schedule.html and logs have been created')
    done_info.pack()


root = Tk()
current_font = font.nametofont("TkDefaultFont")
root.wm_title("EPFL Library desk schedule v" + version)
width = 400
width_chars = int(1.7*width / current_font.actual()['size'])
root.geometry(f'{width}x250+1000+300')

Button(root, text="Sélection du fichier des horaires", command=get_horaire_file).pack()
Button(root, text="Sélection du fichier des absences (optionnel)", command=get_absence_file).pack()

button_label = 'Générer planning'
Button(root, text=button_label, command=partial(run_desk_schedule, root, width_chars)).pack()
root.mainloop()
