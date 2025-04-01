from flask import Blueprint, render_template
import sqlite3
from .auth import admin_required

user_bp = Blueprint('utente', __name__)

def get_utente_dal_db(utente_id):
        conn = sqlite3.connect('usersdb.db')
        cur = conn.cursor()
        cur.execute('SELECT * FROM utenti WHERE id = ?', (utente_id,))
        utente = cur.fetchone()
        cur.close()
        return utente


@user_bp.route('/profilo', methods=['GET','POST'])
def profilo():
    utente = get_utente_dal_db(utente_id=1)

    if utente:
        return render_template("categoria/profilo.html", utente=utente)
    else:
        return render_template("categoria/registrazione.html")