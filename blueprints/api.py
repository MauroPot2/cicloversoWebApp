from flask import Blueprint, jsonify, request, render_template
import sqlite3
from datetime import datetime
from slot import Slot

api_bp = Blueprint('api', __name__)

def get_utente_dal_db(utente_id):
        onn = sqlite3.connect('usersdb.db')
        cursore = conn.cursor()
        cursore.execute('SELECT * FROM utenti WHERE id = ?', (utente_id,))
        utente = cur.fetchone()
        cur.close()
        return utente


@api_bp.route('/slot', methods=['GET'])
def get_slot():
    data_str = request.args.get('data')
    if not data_str:
        return jsonify({"error": "Data mancante"}), 400

    try:
        data_datetime = datetime.strptime(data_str, '%Y-%m-%d').date()
        slot_disponibili = Slot.get_available_slots_by_date(data_datetime)
        slot_dati = [{'orario': slot.orario.strftime('%H:%M'), 'servizio_id': slot.servizio_id} for slot in slot_disponibili]
        return jsonify(slot_dati)
    except ValueError:
        return jsonify({"error": "Formato data non valido"}), 400

@api_bp.route('/slot', methods=['POST'])
def create_slot():
    data = request.json.get('data')
    orario = request.json.get('orario')
    servizio_id = request.json.get('servizio_id')

    try:
        data_datetime = datetime.strptime(data, '%Y-%m-%d').date()
        orario_time = datetime.strptime(orario, '%H:%M').time()

        slot = Slot(data_datetime, orario_time, servizio_id=servizio_id)
        slot.save()

        return jsonify({"messaggio": "Slot creato con successo."})
    except Exception as e:
        return jsonify({"error": f"Errore durante la creazione dello slot: {e}"})

@api_bp.route('/prenota_slot', methods=['POST'])
def prenota_slot_api():
    data = request.json.get('data')
    orario = request.json.get('orario')
    servizio_id = request.json.get('servizio_id')

    try:
        data_datetime = datetime.strptime(data, '%Y-%m-%d').date()
        orario_time = datetime.strptime(orario, '%H:%M').time()

        conn = sqlite3.connect('usersdb.db')
        cursore = conn.cursor()
        cursore.execute("UPDATE slot_disponibili SET disponibile = 0 WHERE data = ? AND orario = ? AND servizio_id = ?",
                       (data_datetime.isoformat(), orario_time.isoformat(), servizio_id))
        conn.commit()
        conn.close()

        return jsonify({"messaggio": "Prenotazione effettuata con successo."})
    except Exception as e:
        return jsonify({"error": f"Errore durante la prenotazione: {e}"})

@api_bp.route('/servizi', methods=['GET'])
def get_servizi():
    conn = sqlite3.connect('usersdb.db')
    cursore = conn.cursor()
    cursore.execute("SELECT id, nome FROM servizi")
    servizi = [{'id': row[0], 'nome': row[1]} for row in cursore.fetchall()]
    conn.close()
    return jsonify(servizi)
    
@api_bp.route('/profilo', methods=['GET','POST'])
def profilo():
    utente = get_utente_dal_db(utente_id=1)

    if utente:
        return render_template("categoria/profilo.html", utente=utente)
    else:
        return render_template("categoria/registrazione.html")