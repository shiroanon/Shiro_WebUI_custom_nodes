import os
from aiohttp import web
from server import PromptServer
import glob
current_dir = os.path.dirname(os.path.abspath(__file__))


outputs_dir = os.path.join(current_dir, '..', 'outputs')

CATEGORY = "api/image"
outputs_dir = os.path.normpath(outputs_dir)
def list_image_files(directory):
   
    image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.bmp', '*.tiff', '*.tif', '*.webp']
    
    image_files = []

    for extension in image_extensions:
        image_files.extend(glob.glob(os.path.join(directory, extension)))
    
    return image_files


@PromptServer.instance.routes.get("/outputs")
async def get_hello(request):
    return web.json_response(list_image_files(outputs_dir))


