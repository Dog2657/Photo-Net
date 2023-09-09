from core.auth.dependencies import get_albem_from_id, getUserFromAccessTokenIfValid, decode_Token
from fastapi import APIRouter, Depends, HTTPException, Request, Form, Response
from core.security.security import verify_password, encodeToken
from core.auth.auth import getAlbemAccessType
from fastapi.responses import HTMLResponse, RedirectResponse
from database.connections import imagesDB
from datetime import datetime, timedelta
from core import templator, environment
from typing import Annotated

router = APIRouter(prefix='/{albemId}')

@router.get('/get-image/{index}')
def GET_Image_By_Index(request: Request, index: int, albem = Depends(get_albem_from_id), account = Depends(getUserFromAccessTokenIfValid)):
    if(imagesDB.count(albemId=albem.get("_id")) <= index):
        raise HTTPException(401, "Invalid image index")
    
    asset = imagesDB.db.findMany({"albemId": albem.get("_id")}, None, skip=index, limit=1)[0]
    if(asset is None):
        raise HTTPException(500, "Unable to get image")
    
    imageData = imagesDB.get(asset.get("_id")).read()
    response = Response(content=imageData, media_type=asset.get('type'))

    if(account):
        if(account.get("_id") == albem.get("owner")):
            return response
        
        if(getAlbemAccessType(albem.get("access"), account.get("_id", None)) is not None):
            return response
         
    if(not albem.get('public')):
        raise HTTPException(401, "This ablem is private and you don't have access" if account else "This albem is on private")

    if(albem.get('password', None) is not None):
        password_access_token = request.cookies.get(f"albem-password-access-{albem.get('_id')}")
        if(password_access_token is None):
            raise HTTPException(400, f"Please password authenticate")

        
        tokenDetails = decode_Token(password_access_token, "albem-password-access")
        if(tokenDetails.get('albemId') != albem.get("_id")):
            raise HTTPException(401, "This token is for another albem")

    return response


@router.api_route('/', methods=["GET", "POST"], response_class=HTMLResponse)
def Get_Albem_Viewer(request: Request, albem = Depends(get_albem_from_id), account = Depends(getUserFromAccessTokenIfValid)):
    details = {
        "totalImages": imagesDB.count(albemId=albem.get("_id")),
        "name": albem.get("name")
    }

    if(account):
        if(account.get("_id") == albem.get("owner")):
            return templator.render('html/albemViewer.html', **details, canEdit=True, isOwner=True)
        
        access_type = getAlbemAccessType(albem.get("access"), account.get("_id", None))
        if(access_type == 'editor'):
            return templator.render('html/albemViewer.html', **details, canEdit=True, isOwner=False)
        
        if(access_type == 'viewer'):
            return templator.render('html/albemViewer.html', **details, canEdit=False, isOwner=False)
        
        del access_type

    if(albem.get('password', None) is not None):
        password_access_token = request.cookies.get(f"albem-password-access-{albem.get('_id')}")
        if(password_access_token is None):
            return templator.render('html/passwordForm.html', albemId=albem.get("_id"))
        
        tokenDetails = decode_Token(password_access_token, "albem-password-access")
        if(tokenDetails.get('albemId') != albem.get("_id")):
            raise HTTPException(401, "This token is for another albem")

    return templator.render('html/albemViewer.html', **details, canEdit=False, isOwner=False)




@router.post('/password_auth')
def POST_Albem_Password_Auth(password: Annotated[str, Form()], albem = Depends(get_albem_from_id)):
    if(albem.get("password", None) is None):
        raise HTTPException(400, "This albem isn't password protected")

    if(not verify_password(password, albem.get("password"))):
        return HTMLResponse(templator.render('html/passwordForm.html', albemId=albem.get("_id"), passwordIncorect=True))
    
    expires = datetime.utcnow() + timedelta(hours= environment.get('Password_Access_Hour', 'int') )

    token = encodeToken({
        "type": "albem-password-access",
        "albemId": albem.get("_id"),
        "exp": expires
    })

    response = RedirectResponse(f'/{albem.get("_id")}')
    response.set_cookie(
        key=f"albem-password-access-{albem.get('_id')}",
        value=token,
        expires=expires.strftime('%a, %d-%b-%Y %T GMT')
    )

    return response