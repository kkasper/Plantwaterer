from flask import Blueprint

bp = Blueprint('errors', __name__)

from WateringSite.errors import handlers