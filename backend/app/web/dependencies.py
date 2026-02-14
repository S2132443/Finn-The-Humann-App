"""Shared dependencies for web routes: templates, flash messages, URL helpers."""

import os
from fastapi import Request
from fastapi.templating import Jinja2Templates

# Template directory
_template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
templates = Jinja2Templates(directory=_template_dir)


def flash(request: Request, message: str, category: str = "info"):
    """Add a flash message to the session."""
    if "_flashes" not in request.session:
        request.session["_flashes"] = []
    request.session["_flashes"].append({"message": message, "category": category})


def get_flashed_messages(request: Request):
    """Pop flash messages from the session."""
    return request.session.pop("_flashes", [])


def _url_for(path: str) -> str:
    """Simple path-based URL helper for templates."""
    return path


# Register template globals
templates.env.globals["url_for"] = _url_for
templates.env.globals["get_flashed_messages"] = get_flashed_messages
