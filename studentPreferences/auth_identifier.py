from django.db.utils import OperationalError, ProgrammingError

from .models import AuthIdentifierSettings


def get_auth_identifier_settings():
    try:
        return AuthIdentifierSettings.get_solo()
    except (OperationalError, ProgrammingError):
        return AuthIdentifierSettings(
            username_mode=AuthIdentifierSettings.MODE_MANUAL,
            username_affix='',
            affix_position=AuthIdentifierSettings.POSITION_SUFFIX,
        )


def get_auth_identifier_context():
    settings_obj = get_auth_identifier_settings()
    affix = (settings_obj.username_affix or '').strip()
    return {
        'enabled': bool(affix),
        'mode': settings_obj.username_mode,
        'uses_manual_username': settings_obj.username_mode == AuthIdentifierSettings.MODE_MANUAL,
        'uses_email_prefix': settings_obj.username_mode == AuthIdentifierSettings.MODE_EMAIL_PREFIX,
        'text': affix,
        'position': settings_obj.affix_position,
        'is_prefix': bool(affix) and settings_obj.affix_position == AuthIdentifierSettings.POSITION_PREFIX,
        'is_suffix': bool(affix) and settings_obj.affix_position == AuthIdentifierSettings.POSITION_SUFFIX,
    }


def get_email_prefix(email):
    email_value = (email or '').strip()
    if '@' not in email_value:
        return ''
    return email_value.split('@', 1)[0].strip()


def strip_auth_identifier_affix(raw_username):
    username = (raw_username or '').strip()
    settings_obj = get_auth_identifier_settings()
    affix = (settings_obj.username_affix or '').strip()

    if not username or not affix:
        return username

    if settings_obj.affix_position == AuthIdentifierSettings.POSITION_PREFIX and username.startswith(affix):
        return username[len(affix):].strip()

    if settings_obj.affix_position == AuthIdentifierSettings.POSITION_SUFFIX and username.endswith(affix):
        return username[:-len(affix)].strip()

    return username


def build_auth_identifier_username(raw_username, email=None):
    settings_obj = get_auth_identifier_settings()
    if settings_obj.username_mode == AuthIdentifierSettings.MODE_EMAIL_PREFIX:
        username = get_email_prefix(email) or strip_auth_identifier_affix(raw_username)
    else:
        username = strip_auth_identifier_affix(raw_username)
    affix = (settings_obj.username_affix or '').strip()

    if not username or not affix:
        return username

    if settings_obj.affix_position == AuthIdentifierSettings.POSITION_PREFIX:
        return f'{affix}{username}'

    return f'{username}{affix}'


def get_auth_identifier_username_candidates(raw_username, email=None):
    raw_value = (raw_username or '').strip()
    normalized_value = build_auth_identifier_username(raw_value, email=email)
    stripped_value = strip_auth_identifier_affix(raw_value)
    email_prefix_value = get_email_prefix(email)

    candidates = []
    for candidate in (normalized_value, stripped_value, raw_value, email_prefix_value):
        if candidate and candidate not in candidates:
            candidates.append(candidate)
    return candidates
