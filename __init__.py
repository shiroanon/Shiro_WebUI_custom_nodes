from .out_request import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS
import os
import server
import glob
def list_image_files(directory):
  
    image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.bmp', '*.tiff', '*.tif', '*.webp']
    
 
    image_files = []

    # Loop through each extension and use glob to find matching files
    for extension in image_extensions:
        # Extend the list with just the file names
        image_files.extend([os.path.basename(file) for file in glob.glob(os.path.join(directory, extension))])
    
    return image_files
from aiohttp import web
@server.PromptServer.instance.routes.get("/dungeon")
def deungeon_entrance(request):
    return web.json_response(list_image_files("outputs"))
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']