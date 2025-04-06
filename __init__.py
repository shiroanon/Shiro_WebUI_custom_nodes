from .out_request import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS
import os
import server
import glob
from PIL import Image
from pathlib import Path
from aiohttp import web

COMPRESSED_DIR = Path('compressed_images')
COMPRESSED_DIR.mkdir(exist_ok=True)



# Define the path to the image
IMAGE_PATH = Path("/tmp/preview.jpg")
import shiro.utils
# Lets manipulate comfy through args switches
from shiro.cli_args import args, LatentPreviewMethod
args.preview_method = LatentPreviewMethod.Latent2RGB
def f(value, total, preview):
		if preview:
			preview[1].save('/tmp/preview.jpg')
shiro.utils.set_progress_bar_global_hook(f)
# Route to serve the image
@server.PromptServer.instance.routes.get("/stream/image")
async def serve_image(request):
    if IMAGE_PATH.exists():
        return web.FileResponse(IMAGE_PATH)
    else:
        return web.json_response({'status': 'error', 'message': 'Image not found.'}, status=404)



__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']