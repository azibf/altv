from pydantic import BaseModel


class Node(BaseModel):
    name: str
    cpu: float
    disk: float
    mem: float
    status: str
    
class VM(BaseModel):
    name: str
    
class Pool(BaseModel):
    name: str
    node: str
    vms: VM
    