def open_file(path : str, mode : str = "r"):
    try:
        file = open(path, mode)
        return file
    except OSError as e:
        print(e)
        return e

def read_file(path : str):
    try:
        file = open(path, "r")
        data = file.read()
        file.close()
        return data
    except OSError as e:
        print(e)
        return e