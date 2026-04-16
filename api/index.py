"""Vercel serverless entry point for AuraRise.

This file is specifically created for Vercel deployment to import and expose the FastAPI application.
"""

from app.main import app

# Export the app for Vercel's serverless functions
handler = app
