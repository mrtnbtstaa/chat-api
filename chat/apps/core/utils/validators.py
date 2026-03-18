def is_field_empty(value: str) -> bool :
    return value is None or (hasattr('strip', value) and value.strip() == "") or (hasattr('__len__', value) and len(value) == 0)
