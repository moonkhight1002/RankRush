from .auth_identifier import get_auth_identifier_context


def auth_identifier(request):
    return {
        'auth_identifier': get_auth_identifier_context(),
    }
