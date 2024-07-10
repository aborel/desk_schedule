import os
import sys
import traceback

# error_output = "desk_schedule_errors.txt"
error_output_header = "This is the desk_schedule log for errors and warnings. Do not archive.\n"

# log_output = "desk_schedule_log.txt"


def log_error_message(error_output, message):
    f_err = open(error_output, "a")
    f_err.write(message + '\n')
    f_err.close()


def log_message(log_output, message):
    f_log = open(log_output, "a")
    f_log.write(message + '\n')
    f_log.close()


def init_error_log(error_output):
	# delete existing logfile unless it doesn't exist
    try:
        os.remove(error_output)
    except OSError:
        pass

    f_err = open(error_output, "w")
    f_err.write(error_output_header)
    f_err.close()


def get_stack_trace(e):
    T, V, TB = sys.exc_info()
    trace = ''.join(traceback.format_exception(T, V, TB))
    return trace


def init_main_log(log_output):
    # delete existing logfile unless it doesn't exist
    try:
        os.remove(log_output)
    except OSError:
        pass

    f_log = open(log_output, "w")
    f_log.close()
