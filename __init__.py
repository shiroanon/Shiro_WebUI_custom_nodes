from .out_request import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS
import os
import server
from aiohttp import web
@server.PromptServer.instance.routes.get("/dungeon")
def deungeon_entrance(request):
    return web.json_response("hello")
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']