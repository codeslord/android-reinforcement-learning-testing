import io
import json

OUTPUT_FOLDER = "../output/"


def write_activity_json_to_files(grouped_events_dict, path=OUTPUT_FOLDER):
    """Write the events to files regarding the activities."""
    for key in grouped_events_dict:
        filename = path + key + ".json"
        with io.FileIO(filename, "w") as file:
            json.dump(grouped_events_dict[key], file)


def write_json_to_jsonfiles(dict, path=OUTPUT_FOLDER):
    """Write json to files."""
    filename = path+"dump.json"
    with io.FileIO(filename, "w") as file:
        json.dump(dict, file)

def write_string_to_file(text, filename="text"):
    """Write string to a file."""
    with io.FileIO(filename, "w") as file:
        file.write(text)
        print 'write:', filename


def append_string_to_file(text, filename="../execlog"):
    """Append string to a file."""
    print 'append string to file'
    with io.FileIO(filename, "a") as file:
        file.write(text+'\n')
