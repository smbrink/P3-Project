def update_name(name, mapping):
    for search_error in mapping:
        if search_error in name:
            name = re.sub(r'\b' + search_error + r'\b\.?', mapping[search_error], name)
    return name