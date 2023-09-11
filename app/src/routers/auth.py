from fastapi import APIRouter, Form, HTTPException, Response, Depends, BackgroundTasks
from core.security.security import verify_password, generateOneTimeCode, hash_password
from database.connections import UserDB, AuthCodesDB, PendingUserDB
from core.auth import auth, dependencies as authDependencies
from core import environment, validation as validate
from datetime import datetime, timedelta
from typing import Annotated
from core import comunicator

router = APIRouter(dependencies=[ Depends(authDependencies.notLoggedIn) ])

@router.post("/login", tags=['Login'])
async def POST_Login(selector: Annotated[str, Form()], password: Annotated[str, Form()], response: Response):
    result = UserDB.findUserByEmail(selector) if (validate.email(selector)) else UserDB.findUserByUsername(selector)
    if(result is None):
        pendingResult = PendingUserDB.find({'$or': [ {"email": selector.lower()}, {"username": {'$regex': f'^{selector}$', "$options": 'i'} } ]})
        if( pendingResult ):
            if(not verify_password(password, pendingResult.get('passwordHash'))):
                raise HTTPException(401, "Password is incorect")
            else:
                return auth.generate_pending_account_token_response( pendingResult.get("_id"), pendingResult.get('email'), pendingResult.get('username'), pendingResult.get('expires') )
            
        del pendingResult
        raise HTTPException(404, "No account with that email/username")
    
    
    if(not verify_password(password, result.get('passwordHash'))):
        raise HTTPException(401, "Password is incorect")
    
    return auth.login_user(response, result.get('_id'))


@router.post("/forgot-password", tags=["Reset Password"])
async def POST_Reset_Password(selector: Annotated[str, Form()], background_tasks: BackgroundTasks):
    background_tasks.add_task(auth.send_password_reset_token, selector)


@router.put('/forgot-password/{token}', tags=["Reset Password"])
async def PUT_Set_Reset_Password(token: str, password: Annotated[str, Form()]):
    details = authDependencies.decode_Token(token, "password_reset")

    account = UserDB.find(id=details.get("userId"))
    if(not account):
        raise HTTPException(404, "The account linked to this token cant be found")

    issuedToken = datetime.fromtimestamp(details.get("issued"))
    if(issuedToken < account.get('lastPasswordChange', issuedToken)):
        raise HTTPException(401, "Token invalidated due to recent password change")
    
    if(verify_password(password, account.get("passwordHash"))):
        raise HTTPException(400, "Password can't be the same")

    if(not validate.password(password)):
        raise HTTPException(400, "Password is week")
    
    UserDB.update({"$set": {
        "passwordHash": hash_password(password),
        "lastPasswordChange": datetime.utcnow()
    }}, id=account.get("_id"))