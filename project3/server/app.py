import asyncio
import time

from fastapi import Depends, FastAPI, HTTPException, Request
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from .resource_hdlr import ResourceHandler, get_resources_hdlr

app = FastAPI()


class ResourceLiberation(BaseModel):
    is_liberated: bool
    resource: int


@app.get("/resource/{resource}/ask")
async def request_resource(
    resource: int,
    client_id: int,
    req: Request,
    serv: ResourceHandler = Depends(get_resources_hdlr),
):
    serv.get_resource(client_id, resource)

    async def resource_getter():
        count = 0
        while True:
            # If client closes connection, stop sending events
            if await req.is_disconnected():
                break
            if serv.owner(resource) != client_id:
                if count % 10:
                    yield "Not liberated"
                count += 1
                await asyncio.sleep(0.1)
            else:
                yield "Liberated"
                break

    return EventSourceResponse(resource_getter())


@app.get("/resource/{resource}/release")
def release_resource(
    resource: int, client_id: int, serv: ResourceHandler = Depends(get_resources_hdlr)
) -> str:
    res = serv.release_resource(client_id, resource)
    if not res:
        raise HTTPException(400, f"Resource {resource} not owned by client {client_id}")
    return "Success"


@app.get("/new_id")
def get_new_client_id(serv: ResourceHandler = Depends(get_resources_hdlr)) -> int:
    return serv.add_client()
