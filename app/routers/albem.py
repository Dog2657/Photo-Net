from core.auth.dependencies import get_albem_from_id, getUserFromAccessTokenIfValid
from fastapi import APIRouter, Depends, HTTPException, Request
from core.auth.auth import getAlbemAccessType
from fastapi.responses import HTMLResponse
from database.connections import imagesDB
from core import templator

router = APIRouter(prefix='/{albemId}')

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

    