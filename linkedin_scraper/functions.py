# coding: utf-8
import re

def time_divide(string):
    duration = re.search("\((.*?)\)", string)

    if duration != None:
        duration = duration.group(0)
        string = string.replace(duration, "").strip()
    else:
        duration = "()"

    times = string.split("–")
    return (times[0].strip(), times[1].strip(), duration[1:-1])
