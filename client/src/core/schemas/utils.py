def title_to_validate(title_str: str) -> str:
    cleaned: str = title_str.strip()

    if not cleaned:
        raise ValueError('Title cannot be empty')

    return cleaned
