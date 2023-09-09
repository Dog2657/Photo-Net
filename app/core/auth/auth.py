from ..security.security import encodeToken, encodeTimeToken
from database.connections import UserDB, AuthCodesDB
from fastapi import Response, HTTPException
from datetime import datetime, timedelta
from .. import environment, comunicator
from datetime import datetime

def login_user(response: Response, userId: str) -> dict:
    expires = datetime.utcnow() + timedelta(hours= environment.get('Access_Lifetime_Hours', 'int') )

    access_token = encodeToken({
        "userId": userId,
        "type": "access",
        "issued": datetime.utcnow().timestamp(),
        "exp": expires
    })

    response.set_cookie(
        key="access_token",
        value=access_token,
        expires=expires.strftime('%a, %d-%b-%Y %T GMT')
    )

    return {
        'type': "access_token",
        'token_expires': expires.strftime("%m/%d/%Y %H:%M:%S")
    }

def getAlbemAccessType(access_list: list, userId: str) -> str | None:
    for access in access_list:
        if(access.get("userId") != userId):
            continue

        return access.get('type')

def generate_pending_account_token_response(userId: str, email: str, username: str, expires: datetime, service: dict = None) -> dict:
    token = encodeToken({
        "userId": userId,
        "type": "pending_account",
        "email": email,
        "username": username,
        "exp": expires,
        "service": service
    })

    return {
        "type": "pending_account",
        "token": token,
        "expires": expires.strftime("%m/%d/%Y %H:%M:%S")
    }


def send_password_reset_token(selector: str) -> None:
    account = UserDB.findUserBySelector(selector)
    if(not account):
        return

    if(AuthCodesDB.find({"type": "forgot-password", "userId": account.get("_id"), "type": "email"})):
        return

    token = encodeTimeToken({
        "type": "password_reset",
        "userId": account.get("_id"),
        "issued": datetime.utcnow().timestamp()
    }, Minutes=environment.get('Password_Reset_Lifetime_Minutes', 'int'))

    #TODO: add front end client password reset uri 

    comunicator.send_email_template(
        "password_reset.html",
        account.get('email'),
        "Reset your password",
        username=account.get("username"),
        link=f"https://yoursite.com/resetpassword/{token}"
    )
    
    AuthCodesDB.insert({
        "type": "forgot-password",
        "userId": account.get("_id"),
        "expires": datetime.utcnow() + timedelta(minutes=environment.get('Password_Reset_Lifetime_Minutes', 'int')),
        "type": "email"
    })