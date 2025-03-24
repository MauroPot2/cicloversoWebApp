from flask import Blueprint, render_template
import sqlite3
from .auth import admin_required

servizi_bp = Blueprint('servizi', __name__)

@servizi_bp.route('/servizi', methods=['GET'])
@admin_required
def gestisci_servizi():
    conn = sqlite3.connect('usersdb.db')
    conn.row_factory = sqlite3.Row
    servizi = conn.execute("SELECT * FROM servizi").fetchall()
    conn.close()
    return render_template('admin/servizi.html', servizi=servizi)