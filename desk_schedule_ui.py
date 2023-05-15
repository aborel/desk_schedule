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

version = "1.0"

error_file = "desk_schedule_errors.txt"


def log_message(message):
    f_err = open(error_file, "a")
    f_err.write(message + '\n')
    f_err.close()


def get_horaire_file(tkroot, width_chars, choosefile):
    filetypes = (
        ('text files', '*.xlsx'),
        ('All files', '*.*')
    )
    d_title = "Choose the Horaires XLSX file"
    choosefile = filedialog.askopenfilename(initialdir=Path.home(), filetypes=filetypes, title=d_title)
    print(choosefile)

def get_absence_file(tkroot, width_chars, choosefile):
    filetypes = (
        ('text files', '*.html'),
        ('All files', '*.*')
    )
    d_title = "Choose the absences.epfl.ch file (saved HTML)"
    choosefile = filedialog.askopenfilename(initialdir=Path.home(), filetypes=filetypes, title=d_title)
    print(choosefile)


def run_desk_schedule(tkroot, width_chars, check_zips):
    # Clear all existing text messages
    do_zips = bool(check_zips.get())
    for label in tkroot.winfo_children():
        if type(label) is Label:
            label.destroy()
    

    error_message = f"There were errors or warnings during processing:\ncheck {error_file} for information."
    error_file_header = "This is the acouachecksum log for errors and warnings. Do not archive.\n"

    d_title = "Select your ingestion folder"
    choosedir = filedialog.askdirectory(initialdir=Path.home(), title=d_title)
    if choosedir == '' or not os.path.exists(choosedir):
        return
    os.chdir(choosedir)

    # delete existing logfile unless it doesn't exist
    try:
        os.remove(error_file)
    except OSError:
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
horaires_var = StringVar()
Button(root, text="Sélection du fichier des horaires", command=partial(get_horaire_file, root, width_chars, horaires_var)).pack()

absences_var = StringVar()
Button(root, text="Sélection du fichier des absences (optionnel)", command=partial(get_absence_file, root, width_chars, absences_var)).pack()

button_label = 'Générer planning'
Button(root, text=button_label, command=partial(run_desk_schedule, root, width_chars, horaires_var, absences_var)).pack()
root.mainloop()
