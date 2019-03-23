from flask import Blueprint

bp = Blueprint('main', __name__)

from WateringSite.main import routes
