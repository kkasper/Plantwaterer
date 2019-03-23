from flask import Blueprint

bp = Blueprint('auth', __name__)

from WateringSite.auth import routes