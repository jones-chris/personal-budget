from flask import Flask

from .api import create_app

gunicorn_app: Flask = create_app()

