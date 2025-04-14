from .out_request import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS
import os
import server
import glob
from PIL import Image
from pathlib import Path
from aiohttp import web
IMAGE_PATH = Path("/tmp/preview.jpg")
IMAGE_DIRECTORY = Path("./output")
def validate_path(filename: str) -> Path | None:
    if not filename or '/' in filename or '\\' in filename or '..' in filename:
        return None

    try:
        potential_path = IMAGE_DIRECTORY / filename
        base_dir_resolved = IMAGE_DIRECTORY.resolve()
        file_path_resolved = potential_path.resolve()

        if not str(file_path_resolved).startswith(str(base_dir_resolved)):
            return None

        return file_path_resolved
    except ValueError:
        return None
    except Exception:
        return None
try :
    import shiro.utils
    from shiro.cli_args import args, LatentPreviewMethod
    args.preview_method = LatentPreviewMethod.Latent2RGB
except:
    import comfy.utils
    from comfy.cli_args import args, LatentPreviewMethod
    args.preview_method = LatentPreviewMethod.Latent2RGB
        
def f(value, total, preview):
		if preview:
			preview[1].save('/tmp/preview.jpg')
shiro.utils.set_progress_bar_global_hook(f)
# Route to serve the image
@server.PromptServer.instance.routes.get("/shiro/preview")
async def serve_image(request):
    if IMAGE_PATH.exists():
        return web.FileResponse(IMAGE_PATH)
    else:
        return web.json_response({'status': 'error', 'message': 'Image not found.'}, status=404)


@server.PromptServer.instance.routes.get("/shiro/image/{filename}")
async def serve_image_by_filename(request: web.Request) -> web.Response:
    filename = request.match_info.get('filename', None)
    if not filename:
        return web.json_response(
            {'status': 'error', 'message': 'Filename parameter is required.'},
            status=400
        )

    file_path_resolved = validate_path(filename)

    if file_path_resolved is None:
         return web.json_response(
             {'status': 'error', 'message': 'Invalid or disallowed filename.'},
             status=400
         )

    if file_path_resolved.is_file():
        return web.FileResponse(file_path_resolved)
    else:
        return web.json_response(
            {'status': 'error', 'message': 'Image not found.'},
            status=404
        )

@server.PromptServer.instance.routes.delete("/shiro/image/{filename}")
async def delete_image_by_filename(request: web.Request) -> web.Response:
    filename = request.match_info.get('filename', None)
    if not filename:
        return web.json_response(
            {'status': 'error', 'message': 'Filename parameter is required.'},
            status=400
        )

    file_path_resolved = validate_path(filename)

    if file_path_resolved is None:
        return web.json_response(
            {'status': 'error', 'message': 'Invalid or disallowed filename.'},
            status=400
        )

    if not file_path_resolved.is_file():
        return web.json_response(
            {'status': 'error', 'message': 'Image not found.'},
            status=404
        )

    try:
        file_path_resolved.unlink()
        return web.json_response(
            {'status': 'success', 'message': f'Image {filename} deleted successfully.'},
            status=200
        )
    except OSError as e:
        return web.json_response(
            {'status': 'error', 'message': f'Could not delete image: {e.strerror}'},
            status=500
        )
    except Exception as e:
        return web.json_response(
            {'status': 'error', 'message': 'Internal server error during deletion.'},
            status=500
        )

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']