from core.auth.dependencies import get_albem_from_id, getUserFromAccessToken
from fastapi import APIRouter, Depends, HTTPException
from database.connections import UserDB

router = APIRouter(prefix='/{albemId}')

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