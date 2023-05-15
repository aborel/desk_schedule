import os

error_file = "desk_schedule_errors.txt"
error_file_header = "This is the desk_schedule log for errors and warnings. Do not archive.\n"


def log_message(message):
    f_err = open(error_file, "a")
    f_err.write(message + '\n')
    f_err.close()


def init_error_log():
	# delete existing logfile unless it doesn't exist
    try:
        os.remove(error_file)
    except OSError:
        pass

    f_err = open(error_file, "w")
    f_err.write(error_file_header)
    f_err.close()

