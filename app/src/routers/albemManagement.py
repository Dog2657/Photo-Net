from core.auth.dependencies import get_albem_from_id, getUserFromAccessToken
from fastapi import APIRouter, Depends, HTTPException, Form
from database.connections import UserDB, albemsDB, imagesDB
from core.security.security import hash_password
from core.auth.auth import getAlbemAccessType
from typing import Annotated

router = APIRouter(prefix='/api/{albemId}')

@router.get("/access-list")
async def GET_Access_List(albem = Depends(get_albem_from_id), account = Depends(getUserFromAccessToken)):
    if(albem.get("owner") != account.get("_id")):
        raise HTTPException(401, "Only the albem owner may use this endpoint")
    
    accessList: list = []
    for access in albem.get('access'):
        user = UserDB.find(id=access.get("userId"))
        accessList.append({
            "userId": user.get("_id"),
            "username": user.get("username"),
            "email": user.get("email"),
            "type": access.get('type')
        })
   
    return accessList


@router.post('/add-access')
async def POST_Add_Access(userSelector: str, access: str, albem = Depends(get_albem_from_id), account = Depends(getUserFromAccessToken)):
    if(albem.get("owner") != account.get("_id")):
        raise HTTPException(401, "Only the albem owner may use this endpoint")
    
    user = UserDB.findUserBySelector(userSelector)
    if(user is None):
        raise HTTPException(404, "No user found with this email/username")

    if(access.lower() not in ['viewer', 'editor']):
        raise HTTPException(400, "Not a valid access type (viewer or editor)")

    if(getAlbemAccessType(albem.get('access'), user.get("_id")) is not None):
        raise HTTPException(400, "This user already has aceess")

    albemsDB.update({"$push": {"access": {"userId": user.get("_id"), "type": access.lower()}}}, id=albem.get("_id"))

    return {
        "userId": user.get("_id"),
        "username": user.get("username"),
        "email": user.get("email"),
        "type": access.lower()
    }


@router.patch('/update-access')
async def PATCH_Access_Type(userId: str, access: str, albem = Depends(get_albem_from_id), account = Depends(getUserFromAccessToken)):
    if(albem.get("owner") != account.get("_id")):
        raise HTTPException(401, "Only the albem owner may use this endpoint")
    
    user = UserDB.find(id=userId)
    if(user is None):
        raise HTTPException(404, "No user found with this id")
    
    if(access.lower() not in ['none', 'viewer', 'editor']):
        raise HTTPException(400, "Not a valid access type (none or viewer or editor)")

    if(getAlbemAccessType(albem.get('access'), user.get("_id")) is None):
        raise HTTPException(400, "User dosn't have any access")

    if(access.lower() == 'none'):
        albemsDB.update({"$pull": {"access": {"userId": user.get("_id")}}}, id=albem.get("_id"))

    else:
        albemsDB.update({"$set": {"access.$.type": access.lower()}}, {'access.userId': user.get("_id")}, id=albem.get("_id"))



@router.patch('/set-link-password')
async def PATCH_Set_Link_Password(password: Annotated[str, Form()] = "", albem = Depends(get_albem_from_id), account = Depends(getUserFromAccessToken)):
    if(albem.get("owner") != account.get("_id")):
        raise HTTPException(401, "Only the albem owner may use this endpoint")

    if(password == ""):
        albemsDB.update({"$unset": {"password": 1}}, id=albem.get("_id"))
        return {"detail": "Password removed"}
    
    else:
        albemsDB.update({"$set": {"password": hash_password(password)}}, id=albem.get("_id"))
        return {"detail": "Password updated"}
    

@router.put('/update')
async def PUT_Update_Albem_Details(public: bool, name: str = "", albem = Depends(get_albem_from_id), account = Depends(getUserFromAccessToken)):
    if(albem.get("owner") != account.get("_id")):
        raise HTTPException(401, "Only the albem owner may use this endpoint")
    
    if(name == ""):
        raise HTTPException(400, "Name can't be blank")
    
    albemsDB.update({"$set": {"name": name, "public": public}})



@router.delete('/delete-image/{index}')
async def DELETE_Image(index: int, albem = Depends(get_albem_from_id), account = Depends(getUserFromAccessToken)):
    if(
        albem.get("owner") != account.get("_id") and
        getAlbemAccessType(albem.get("access"), account.get("_id", None)) != "editor"
    ):
        raise HTTPException(401, "You don't have the editor permission")
    
    if(imagesDB.count(albemId=albem.get("_id")) <= index):
        raise HTTPException(401, "Invalid image index")

    assetId = imagesDB.db.findMany({"albemId": albem.get("_id")}, None, skip=index, limit=1)[0].get("_id", None)
    if(assetId is None):
        raise HTTPException(500, "Unable to get image")
    
    imagesDB.delete(assetId)

    albemId = albem.get('_id')