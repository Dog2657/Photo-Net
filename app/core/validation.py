from email_validator import validate_email, EmailNotValidError
import phonenumbers

def email(address: str) -> bool:
    try:
        validate_email(address)
        return True
    except EmailNotValidError as e:
        return False

def password(value: str) -> bool:
    #TODO: add password checks
    return True