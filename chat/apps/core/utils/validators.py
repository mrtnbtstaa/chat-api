def is_field_empty(value: str) -> bool :
    return value is None or (hasattr('strip') and value.strip() == "") or (hasattr('__len__') and len(value) == 0)
