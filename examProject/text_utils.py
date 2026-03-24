import re


def normalize_title_case(value):
    if not isinstance(value, str):
        return value

    cleaned = re.sub(r"\s+", " ", value).strip()
    if not cleaned:
        return cleaned

    return " ".join(word[:1].upper() + word[1:].lower() for word in cleaned.split(" "))


def split_full_name(value):
    normalized = normalize_title_case(value)
    if not normalized:
        return "", ""

    parts = normalized.split(" ", 1)
    first_name = parts[0]
    last_name = parts[1] if len(parts) > 1 else ""
    return first_name, last_name
