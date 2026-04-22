from django.core.exceptions import ValidationError


PASSWORD_REQUIREMENTS = (
    "At least 6 characters",
    "One uppercase letter",
    "One lowercase letter",
    "One number",
    "One special character",
)

PASSWORD_REQUIREMENTS_TEXT = (
    "Password must be at least 6 characters long and include an uppercase letter, "
    "a lowercase letter, a number, and a special character."
)
PASSWORD_REQUIREMENTS_TITLE = "Use 6+ characters with upper, lower, number, and special character."

PASSWORD_PATTERN = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{6,}$"


def validate_signup_password(password):
    password = password or ""

    if len(password) < 6:
        raise ValidationError(PASSWORD_REQUIREMENTS_TEXT)
    if not any(char.isupper() for char in password):
        raise ValidationError(PASSWORD_REQUIREMENTS_TEXT)
    if not any(char.islower() for char in password):
        raise ValidationError(PASSWORD_REQUIREMENTS_TEXT)
    if not any(char.isdigit() for char in password):
        raise ValidationError(PASSWORD_REQUIREMENTS_TEXT)
    if not any(not char.isalnum() for char in password):
        raise ValidationError(PASSWORD_REQUIREMENTS_TEXT)

    return password


def build_signup_password_widget_attrs(extra_attrs=None):
    attrs = {
        "minlength": "6",
        "autocomplete": "new-password",
        "pattern": PASSWORD_PATTERN,
        "title": PASSWORD_REQUIREMENTS_TITLE,
        "data-password-rules": " | ".join(PASSWORD_REQUIREMENTS),
    }
    if extra_attrs:
        attrs.update(extra_attrs)
    return attrs
