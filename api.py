from typing import Union
from fastapi import FastAPI, Depends, HTTPException, status, Header, Response, Cookie
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import RedirectResponse
import secrets
import uuid
from typing import Annotated, Any
from time import time
from starlette.responses import JSONResponse
from proxmoxer import ProxmoxAPI
import uvicorn


from db.db import *


app = FastAPI()
security = HTTPBasic()


@app.get("/basic-auth/")
def demo_basic_auth_credentials(credentials: Annotated[User, Depends(security)],):
    credentials.connection = ProxmoxAPI('77.106.68.24', user=f'{credentials.username}@pam', password=credentials.password, verify_ssl=False, service='PVE')
    for i, node in enumerate(proxmox.nodes.get()):
        print(f"{i+1} - {node['node']}")
    return {
        "message": "Hi!",
        "nodes": credentials.connection.nodes.get()
    }

@app.get("/logout")
def logout(response : Response):
    credentials.username = None
    credentials.password = None
    response = RedirectResponse('/basic-auth/', status_code= 302)
    return response

@app.get("/node")
async def getAllNodes():
    proxmox = ProxmoxAPI('77.106.68.24', user='root@pam', password='L57uVaFjDLq9', verify_ssl=False, service='PVE')
    node_list = []
    for i, node in enumerate(proxmox.nodes.get()):
        node_list.append({
            'name': node['node'], 
            'used_mem': node['mem'] * 100 // node['maxmem'],
            'used_cpu': node['cpu'] * 100 // node['maxcpu'],
            'used_disk': node['disk'] * 100 // node['maxdisk'],
            'status': node['status'],
        })
    return node_list

@app.get("/node/{node_name}")
async def getOneNode(node_name: str):
    proxmox = ProxmoxAPI('77.106.68.24', user='root@pam', password='L57uVaFjDLq9', verify_ssl=False, service='PVE')
    for node in proxmox.nodes.get():
        if node['node'] == node_name:
            return JSONResponse({
                'name': node['node'], 
                'used_mem': node['mem'] * 100 // node['maxmem'],
                'used_cpu': node['cpu'] * 100 // node['maxcpu'],
                'used_disk': node['disk'] * 100 // node['maxdisk'],
                'max_mem': node['maxmem'], 
                'max_cpu': node['maxcpu'], 
                'max_disk': node['maxdisk'],
                'status': node['status'],
            })
    return JSONResponse({'error': 'no node'})

@app.get("/vm") 
async def getAllVM():
    proxmox = ProxmoxAPI('77.106.68.24', user='root@pam', password='L57uVaFjDLq9', verify_ssl=False, service='PVE')
    vm_list = []
    for node in proxmox.nodes.get():
        cur_node = proxmox.nodes(node['node'])
        for i, vm in enumerate(cur_node.qemu.get()):
            vm_list.append({
                'name': vm['name'],
                'status' : vm['status']  
            })
    return vm_list

@app.get("/node/{node_name}/vm")
async def getAllVMOnNode(node_name: str):
    proxmox = ProxmoxAPI('77.106.68.24', user='root@pam', password='L57uVaFjDLq9', verify_ssl=False, service='PVE')
    vm_list = []
    cur_node = proxmox.nodes(node_name)
    for i, vm in enumerate(cur_node.qemu.get()):
        vm_list.append({
            'id': vm['vmid'],
            'name': vm['name'],
            'status' : vm['status']  
        })
    return vm_list

@app.get("/node/{node_name}/vm/{vm_id}")
async def getOneVM(node_name: str, vm_id: int):
    proxmox = ProxmoxAPI('77.106.68.24', user='root@pam', password='L57uVaFjDLq9', verify_ssl=False, service='PVE')
    for vm in proxmox.nodes(node_name).qemu.get():
        if vm['vmid'] == vm_id:
            return JSONResponse({
                'id': vm_id,
                'name': vm['name'], 
                'used_mem': vm['mem'] * 100 // vm['maxmem'],
                'used_cpu': vm['cpu'] * 100 // vm['cpus'],
                'used_disk': vm['disk'] * 100 // vm['maxdisk'],
                'max_mem': vm['maxmem'], 
                'max_cpu': vm['cpus'], 
                'max_disk': vm['maxdisk'],
                'status': vm['status'],
            })
    return JSONResponse({'error': 'no vm'})


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/pool")
async def getAllPools(db: Session = Depends(get_db)):
    return db.query(Pool).fetchall()

    

if __name__=="__main__":
    uvicorn.run("api:app", reload=True)