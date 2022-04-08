def remove_none_string(string):
    string = str(string)
    if string == "None" or string == "none" or string == "null" or string == "nil":
        return None
    return string
