from flask import Blueprint, render_template
import sqlite3
from .auth import admin_required

servizi_bp = Blueprint('servizi', __name__)

