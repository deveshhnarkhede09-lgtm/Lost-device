"""
api/index.py - Vercel Serverless Function Entrypoint
Routes all serverless requests into the Flask WSGI application instance.
"""

import sys
import os

# Ensure project root is in sys.path so modules (app, database, matcher) can be resolved
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app import app

# Vercel discovers and invokes the `app` WSGI callable
app = app
