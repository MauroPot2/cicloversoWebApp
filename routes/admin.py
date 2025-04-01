from flask import Blueprint, render_template, jsonify, request, session, flash
from .auth import admin_required
from slot import Slot
import sqlite3
from datetime import datetime, time

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
### Templates route Admin###
@admin_bp.route('/', methods=['GET'])
@admin_required
def admin():
    conn = sqlite3.connect('usersdb.db')
    cursore = conn.cursor()
    cursore.execute("SELECT * FROM utenti WHERE id = ?", (session['user_id'],))
    admin_utente = cursore.fetchone()
    conn.close()
    return render_template("admin/admin_index.html", admin_utente=admin_utente)
    
@admin_bp.route('/crea_slot', methods=['GET'])
@admin_required
def crea_slot():
    conn = sqlite3.connect('usersdb.db')
    conn.row_factory = sqlite3.Row
    servizi = conn.execute("SELECT id, Servizio FROM servizi").fetchall()
    conn.close()
    
    return render_template("admin/crea_slot.html", servizi=servizi)

@admin_bp.route('/prenotazioni', methods=['GET'])
@admin_required
def gestisci_prenotazioni():
    conn = sqlite3.connect('usersdb.db')
    conn.row_factory = sqlite3.Row
    prenotazioni = conn.execute("SELECT * FROM prenotazione").fetchall()
    conn.close()
    return render_template('admin/prenotazioni.html', prenotazioni=prenotazioni)

@admin_bp.route('/utenti', methods=['GET'])
@admin_required
def gestisci_utenti():
    conn = sqlite3.connect('usersdb.db')
    conn.row_factory = sqlite3.Row
    utenti = conn.execute("SELECT * FROM utenti").fetchall()
    conn.close()
    return render_template('admin/utenti.html', utenti=utenti)

@admin_bp.route('/servizi', methods=['GET'])
@admin_required
def gestisci_servizi():
    conn = sqlite3.connect('usersdb.db')
    conn.row_factory = sqlite3.Row
    servizi = conn.execute("SELECT * FROM servizi").fetchall()
    conn.close()
    return render_template('admin/servizi.html', servizi=servizi)
