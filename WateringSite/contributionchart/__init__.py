from flask import Blueprint

bp = Blueprint('contributionchart', __name__)

from WateringSite.contributionchart import render_html
