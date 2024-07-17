import os
import server
from aiohttp import web

import glob
current_dir = os.path.dirname(os.path.abspath(__file__))
@server.PromptServer.instance.routes.get("/dungeon")
def deungeon_entrance(request):
    return web.json_response("hello"))

outputs_dir = os.path.join(current_dir, '..', 'outputs')

outputs_dir = os.path.normpath(outputs_dir)
def list_image_files(directory):
   
    image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.bmp', '*.tiff', '*.tif', '*.webp']
    
    image_files = []

    for extension in image_extensions:
        image_files.extend(glob.glob(os.path.join(directory, extension)))
    
    return image_files


__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
