"""Dashboard web module for user-specific interfaces.

This module implements the dashboard interface routes, handling user-specific
views such as resume management, profile settings, and personalized features
that require user context.
"""

from fastapi import Path, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.web.base_router import WebRouter
from app.core.security import require_login_redirect

web_router = WebRouter()
templates = Jinja2Templates(directory="app/templates")


@web_router.get(
    "/dashboard",
    summary="Dashboard",
    response_description="User dashboard showing resumes and statistics",
    response_class=HTMLResponse,
)
async def dashboard(
    request: Request,
):
    """Render the user dashboard."""
    redirect = require_login_redirect(request)
    if redirect:
        return redirect
    return templates.TemplateResponse("dashboard.html", {"request": request})


@web_router.get(
    "/create",
    summary="Create Resume",
    response_description="Create a new resume",
    response_class=HTMLResponse,
)
async def create_resume(
    request: Request,
):
    """Render the resume creation page."""
    redirect = require_login_redirect(request)
    if redirect:
        return redirect
    return templates.TemplateResponse("create.html", {"request": request})


@web_router.get(
    "/resume/{resume_id}",
    summary="View Resume",
    response_description="View a specific resume",
    response_class=HTMLResponse,
)
async def view_resume(
    request: Request,
    resume_id: str = Path(..., title="Resume ID"),
):
    """Render the detailed view of a specific resume."""
    redirect = require_login_redirect(request)
    if redirect:
        return redirect
    return templates.TemplateResponse(
        "resume_view.html", {"request": request, "resume_id": resume_id}
    )


@web_router.get(
    "/resume/{resume_id}/optimize",
    summary="Optimize Resume",
    response_description="Optimize a specific resume",
    response_class=HTMLResponse,
)
async def optimize_resume_page(
    request: Request,
    resume_id: str = Path(..., title="Resume ID"),
):
    """Render the resume optimization page."""
    redirect = require_login_redirect(request)
    if redirect:
        return redirect
    return templates.TemplateResponse(
        "resume_optimize.html",
        {
            "request": request,
            "resume_id": resume_id,
            "page_title": "Optimize Resume",
        },
    )


@web_router.get(
    "/settings",
    summary="Settings",
    response_description="Manage your settings",
    response_class=HTMLResponse,
)
async def settings(
    request: Request,
):
    """Render the user settings page."""
    redirect = require_login_redirect(request)
    if redirect:
        return redirect
    return templates.TemplateResponse("settings.html", {"request": request})
