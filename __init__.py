from .out_request import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS
import os
import server
import glob
def list_image_files(directory):
    # List of common image file extensions
    image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.bmp', '*.tiff', '*.tif', '*.webp']
    
    # Initialize an empty list to store image file paths
    image_files = []

    # Loop through each extension and use glob to find matching files
    for extension in image_extensions:
        image_files.extend(glob.glob(os.path.join(directory, extension)))
    
    # Sort files by modification time, newest first
    image_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    
    # Extract just the file names
    image_file_names = [os.path.basename(file) for file in image_files]

    return image_file_names
from aiohttp import web
@server.PromptServer.instance.routes.get("/dungeon")
def deungeon_entrance(request):
    return web.json_response(list_image_files("outputs"))
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']