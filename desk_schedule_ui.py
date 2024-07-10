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
from errors import error_output_header, init_error_log, log_error_message, get_stack_trace
import or_librarydesk_schedule

version = "1.1"

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
    html_output = horaires.replace('.xlsx', '') + '.html'
    html_file = html_output.split(os.sep)[-1]

    log_output = horaires.replace('.xlsx', '') + '_log.txt'
    log_file = log_output.split(os.sep)[-1]

    error_output = horaires.replace('.xlsx', '') + '_errors.txt'
    error_file = error_output.split(os.sep)[-1]

    error_message = f"There were errors or warnings during processing:\ncheck {error_file} for information."

    init_error_log(error_output)
    
    if absences is not None:
        if absences != '':
            parse_absences(absences)

    if horaires is not None:
        try:
            or_librarydesk_schedule.main(horaires, log_output, error_output)
        except Exception as e:
            log_error_message(error_output, get_stack_trace(e))
    else:
        log_error_message(log_output, 'Vous DEVEZ sélectionner un fichier XLSX contenant les horaires!')

    f_err = open(error_output, "r")
    error_content = f_err.read()
    f_err.close()
    
    if error_content.replace('\r', '').replace('\n', '') == error_output_header.replace('\r', '').replace('\n', ''):
        os.remove(error_output)
        done_text = f'Done: {html_output_filename} has been created.'
        done_text += '\nCheck the logfile for more details'
        done_info = Label(tkroot, text=done_text)
        done_info.pack()

    else:
        error_info = Label(tkroot, text=error_message)
        error_info.pack()

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
