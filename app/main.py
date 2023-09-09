from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI

from routers.auth import router as AuthRouter
from routers.registration import router as registrationRouter
from routers.accountDetails import graphql_app as accountDetailsRouter
from routers.account import router as accountRouter
from routers.albem import router as albemRouter

app = FastAPI()

with open('../Allowed_Origins.txt') as file:
    origins = file.read().split('\n')
    
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(AuthRouter)
app.include_router(registrationRouter)
app.include_router(accountRouter)
app.include_router(albemRouter)
app.include_router(accountDetailsRouter, prefix="/graphql/account-details", tags=["Get User Details"])