from fastapi import APIRouter, UploadFile, Depends, Request, HTTPException, WebSocket, WebSocketDisconnect
from core.auth.dependencies import get_albem_from_id, getUserFromAccessToken, getUserFromAccessTokenIfValid
from database.connections import albemsDB, imagesDB
from core.auth.auth import getAlbemAccessType
from database.db import formatId
from typing import List


class UploadStatusManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    def register(self, ip: str, albem: str, websocket: WebSocket):
        self.active_connections.append({
            "ip": ip,
            "albemId": albem,
            "websocket": websocket
        })

    async def getConnection(self, ip: str, albem: str):
        for connection in self.active_connections:
            if(connection.get('albemId') != albem):
                continue

            if(connection.get("ip") != ip):
                continue
            
            return connection

    def disconnect(self, websocket: WebSocket):
        for connection in self.active_connections:
            if(connection.get('websocket') is websocket):
                self.active_connections.remove(connection)
                return

    async def updateFileStatus(self, ip: str, albem: str, index: int, state: str):
        connection = await self.getConnection(ip, albem)
        await (connection.get("websocket")).send_json({"index": index, "state": state})

    async def finish(self, ip: str, albem: str):
        connection = await self.getConnection(ip, albem)
        self.active_connections.remove(connection)
        await connection.get('websocket').close()

        




router = APIRouter(prefix='/api/{albemId}')
manager = UploadStatusManager()

@router.websocket("/live-upload-statuses")
async def websocket_endpoint(websocket: WebSocket, albemId: str, account = Depends(getUserFromAccessTokenIfValid)):
    await websocket.accept()

    albem_id = formatId(albemId)
    if(albem_id is None):
        await websocket.close(code=1008, reason="Invalid albem id")
    
    albem = albemsDB.find(id=albem_id)
    if(albem is None):
        await websocket.close(code=1008, reason="Albem not found")

    if(account is None):
        await websocket.close(code=1008, reason="Please login to use this websocket")

    if(
        albem.get("owner") != account.get("_id") and
        getAlbemAccessType(albem.get("access"), account.get("_id", None)) != "editor"
    ):
        await websocket.close(code=1008, reason="You don't have the editor permission")
    
    
    manager.register(websocket.client.host, albem.get("_id"), websocket)

    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)



@router.post('/upload-images')
async def POST_Upload_Images(request: Request, files: List[UploadFile], albem = Depends(get_albem_from_id), account = Depends(getUserFromAccessToken)):
    if(
        albem.get("owner") != account.get("_id") and
        getAlbemAccessType(albem.get("access"), account.get("_id", None)) != "editor"
    ):
        raise HTTPException(401, "You don't have the editor permission")
     

    for index, file in enumerate(files):
        split = file.content_type.split('/')
        
        if(split[0] != 'image' or split[1] not in ['jpeg', 'png']):
            await manager.updateFileStatus(request.client.host, albem.get("_id"), index, "failed")
            continue

        imagesDB.upload(await file.read(), albemId=albem.get("_id"), type=file.content_type)
        await manager.updateFileStatus(request.client.host, albem.get("_id"), index, "success")
        

    await manager.finish(request.client.host, albem.get("_id"))