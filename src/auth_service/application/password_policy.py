from src.auth_service.application.constants import (
    PASSWORD_MAX_LENGTH,
    PASSWORD_MIN_LENGTH,
    PASSWORD_REQUIRED_CLASSES,
)


class PasswordPolicyError(ValueError):
    pass


def validate_password_policy(password: str) -> None:
    if len(password) < PASSWORD_MIN_LENGTH:
        raise PasswordPolicyError(
            f"Password must be at least {PASSWORD_MIN_LENGTH} characters long"
        )
    if len(password) > PASSWORD_MAX_LENGTH:
        raise PasswordPolicyError(
            f"Password must be at most {PASSWORD_MAX_LENGTH} characters long"
        )

    character_classes = sum(
        (
            any(char.islower() for char in password),
            any(char.isupper() for char in password),
            any(char.isdigit() for char in password),
            any(not char.isalnum() for char in password),
        )
    )
    if character_classes < PASSWORD_REQUIRED_CLASSES:
        raise PasswordPolicyError(
            "Password must include at least three of: "
            "lowercase, uppercase, digit, symbol"
        )

    if password.strip() != password:
        raise PasswordPolicyError("Password must not start or end with whitespace")
