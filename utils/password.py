def password_validator(
    min_length: int = 8,
    lower: bool = False,
    capital: bool = False,
    special: bool = False,
):
    def decorator(func):
        def wrapper(password: str):
            # Check minimum length
            if len(password) < min_length:
                return f"Password must be at least {min_length} characters long."

            # Check for lowercase requirement
            if lower and not any(c.islower() for c in password):
                return "Password must contain at least one lowercase letter."

            # Check for uppercase requirement
            if capital and not any(c.isupper() for c in password):
                return "Password must contain at least one uppercase letter."

            # Check for special character requirement
            if special and not any(c in "!@#$%^&*()-_+=<>?" for c in password):
                return "Password must contain at least one special character."

            # If all checks are passed, call the original function (callback)
            return func(password)

        return wrapper

    return decorator

