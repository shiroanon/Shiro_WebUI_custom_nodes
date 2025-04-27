from .out_request import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS
import os
import server
import glob
from PIL import Image
import io
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

try:
    import shiro.utils
    from shiro.cli_args import args, LatentPreviewMethod
    args.preview_method = LatentPreviewMethod.Latent2RGB
except:
    import comfy.utils
    from comfy.cli_args import args, LatentPreviewMethod
    args.preview_method = LatentPreviewMethod.Latent2RGB

def f(value, total, preview):
    if preview and preview[1]:
        try:
            preview[1].save(IMAGE_PATH, 'JPEG')
        except Exception as e:
            print(f"Error saving preview image: {e}")

try:
    shiro.utils.set_progress_bar_global_hook(f)
except NameError:
    try:
        comfy.utils.set_progress_bar_global_hook(f)
    except NameError:
        print("Warning: Could not set global progress bar hook (neither shiro.utils nor comfy.utils found). Preview image generation might not work.")
    except AttributeError:
        print("Warning: Could not set global progress bar hook (set_progress_bar_global_hook not found). Preview image generation might not work.")

@server.PromptServer.instance.routes.get("/shiro/preview")
async def serve_preview(request):
    if IMAGE_PATH.exists():
        return web.FileResponse(IMAGE_PATH)
    else:
        return web.json_response({'status': 'error', 'message': 'Preview image not found.'}, status=404)

@server.PromptServer.instance.routes.get("/shiro/preview/webp")
async def serve_webp_preview(request):
    if not IMAGE_PATH.exists():
        return web.json_response({'status': 'error', 'message': 'Preview image not found.'}, status=404)
    try:
        img = Image.open(IMAGE_PATH)
        buffer = io.BytesIO()
        img.save(buffer, format="WEBP", quality=80)
        buffer.seek(0)
        return web.Response(
            body=buffer.getvalue(),
            content_type='image/webp',
            status=200
        )
    except FileNotFoundError:
         return web.json_response({'status': 'error', 'message': 'Preview image file disappeared.'}, status=404)
    except Exception as e:
        print(f"Error generating WEBP preview: {e}")
        return web.json_response(
            {'status': 'error', 'message': f'Could not generate WEBP preview: {e}'},
            status=500
        )

@server.PromptServer.instance.routes.get("/shiro/image")
async def serve_image_list(request):
    file_list = []
    try:
        IMAGE_DIRECTORY.mkdir(parents=True, exist_ok=True) # Ensure directory exists
        for f_path in IMAGE_DIRECTORY.glob('*'):
            if f_path.is_file():
                file_list.append(f_path.name)
    except Exception as e:
        print(f"Error listing images: {e}")
        return web.json_response({'status': 'error', 'message': 'Error listing images.'}, status=500)

    return web.json_response(
        {'file_list': file_list},
        status=200
    )

@server.PromptServer.instance.routes.get("/shiro/image/search/{search_string}")
async def search_image_by_filename(request: web.Request) -> web.Response:
    search_string = request.match_info.get('search_string', None)
    if not search_string:
        return web.json_response(
            {'status': 'error', 'message': 'Search string parameter is required.'},
            status=400
        )

    file_list = []
    try:
        IMAGE_DIRECTORY.mkdir(parents=True, exist_ok=True) # Ensure directory exists
        for f_path in IMAGE_DIRECTORY.glob(f'{search_string}*'):
            if f_path.is_file():
                if str(f_path.resolve()).startswith(str(IMAGE_DIRECTORY.resolve())):
                    file_list.append(f_path.name)
    except Exception as e:
        print(f"Error searching images: {e}")
        return web.json_response({'status': 'error', 'message': 'Error searching images.'}, status=500)

    return web.json_response(
        {'file_list': file_list},
        status=200
    )

@server.PromptServer.instance.routes.get("/shiro/image/{filename}")
async def serve_image_by_filename(request: web.Request) -> web.Response:
    filename = request.match_info.get('filename', None)
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
            {'status': 'error', 'message': 'Image not found or is not a file.'},
            status=404
        )

@server.PromptServer.instance.routes.get("/shiro/image/webp/{filename}")
async def serve_webp_image_by_filename(request: web.Request) -> web.Response:
    filename = request.match_info.get('filename', None)
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
        img = Image.open(file_path_resolved)
        buffer = io.BytesIO()
        quality = int(request.query.get('quality', 80)) # Optional quality query param
        quality = max(0, min(100, quality)) # Clamp quality between 0-100

        img.save(buffer, format="WEBP", quality=quality)
        buffer.seek(0)
        return web.Response(
            body=buffer.getvalue(),
            content_type='image/webp',
            status=200
        )
    except FileNotFoundError:
         return web.json_response({'status': 'error', 'message': 'Image file disappeared.'}, status=404)
    except UnidentifiedImageError:
         return web.json_response({'status': 'error', 'message': 'Cannot identify image file. It might be corrupted or not an image.'}, status=400)
    except Exception as e:
        print(f"Error generating WEBP for {filename}: {e}")
        return web.json_response(
            {'status': 'error', 'message': f'Could not generate WEBP image: {e}'},
            status=500
        )


@server.PromptServer.instance.routes.delete("/shiro/image/{filename}")
async def delete_image_by_filename(request: web.Request) -> web.Response:
    filename = request.match_info.get('filename', None)
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
        print(f"Deleted image: {filename}")
        return web.json_response(
            {'status': 'success', 'message': f'Image {filename} deleted successfully.'},
            status=200
        )
    except OSError as e:
        print(f"Error deleting image {filename}: {e}")
        return web.json_response(
            {'status': 'error', 'message': f'Could not delete image: {e.strerror}'},
            status=500
        )
    except Exception as e:
        print(f"Unexpected error deleting image {filename}: {e}")
        return web.json_response(
            {'status': 'error', 'message': 'Internal server error during deletion.'},
            status=500
        )

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
