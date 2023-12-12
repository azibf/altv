from typing import Union
from fastapi import FastAPI
from starlette.responses import JSONResponse

'''1) method GET /allNodes - получение всех нод (главная вкладка) (префикс можешь сама придумать)))

2) method GET /containers - получение всех контейнеров (вкладка "pull"), тут ты отправляешь только информацию необходимую для таблицы

3) method GET /containers/${pullId} - получение одного конкретного контейнера по id, тут ты выгружаешь всю возможную информацию о контейнере, включая бд'''


from models import *


app = FastAPI()



@app.get("/allNodes")
async def getAllNodes():
    return JSONResponse({'hello': 'world'})

@app.get("/containers")
async def getAllNodes():
    return JSONResponse({'hello': 'world'})

@app.get("/containers/{pullId} ")
async def getOneNode(pullId: int):
    return JSONResponse({'hello': 'world'})

@app.post("/createContainers")
async def postOneNode():
    return JSONResponse({'hello': 'world'})