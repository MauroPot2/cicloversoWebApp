from flask import Blueprint, jsonify, request, session
from datetime import datetime
from dateutil.parser import parse
import sqlite3
from slot import Slot

api_bp = Blueprint('api', __name__)

#connessione semplice
def get_db_connection():
    conn = sqlite3.connect('usersdb.db')
    conn.row_factory = sqlite3.Row
    return conn

#Recupera tutti i servizi disponibili
@api_bp.route('/servizi', methods=['GET'])
def get_servizi():
    conn = get_db_connection()
    servizi = conn.execute("SELECT id, Servizio FROM servizi").fetchall()
    conn.close()
    return jsonify([{'id': s['id'], 'nome': s['nome']} for s in servizi])

#Recupera slot disponibili
@api_bp.route('/slot', methods=['GET'])
def get_slots():
    start_str = request.args.get('start')
    end_str = request.args.get('end')

    if not start_str or not end_str:
        return jsonify({'error': 'Parametri "start" e "end" mancanti'}), 400

    try:
        from dateutil.parser import parse
        start_date = parse(start_str).date()
        end_date = parse(end_str).date()
    except Exception as e:
        return jsonify({'error': f'Formato data non valido: {e}'}), 400

    conn = sqlite3.connect('usersdb.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Estrai gli slot per il range di date richiesto
    cur.execute('''
        SELECT id, data, ora_inizio, ora_fine, servizio_id
        FROM slot
        WHERE data BETWEEN ? AND ? AND disponibile = 1
    ''', (start_date.isoformat(), end_date.isoformat()))
    rows = cur.fetchall()
    conn.close()

    # Prepara gli eventi per FullCalendar
    events = []
    for row in rows:
        events.append({
            "id": row["id"],
            "data": row["data"],
            "ora_inizio": row["ora_inizio"],
            "ora_fine": row["ora_fine"],
            "servizio_id": row["servizio_id"],
            "title": f"Servizio {row['servizio_id']}"
        })

    return jsonify(events)


#Crea uno slot disponibile
@api_bp.route('/slot', methods=['POST'])
def create_slot():
    data = request.get_json()

    try:
        giorno = data.get('data')                  
        ora_inizio = data.get('ora_inizio')        
        ora_fine = data.get('ora_fine')            
        servizio_id = int(data.get('servizio'))    

        if not (giorno and ora_inizio and ora_fine and servizio_id):
            return jsonify({'error': 'Tutti i campi sono obbligatori'}), 400

        conn = sqlite3.connect('usersdb.db')
        conn.execute('''
            INSERT INTO slot (data, ora_inizio, ora_fine, servizio_id, disponibile)
            VALUES (?, ?, ?, ?, 1)
        ''', (giorno, ora_inizio, ora_fine, servizio_id))
        conn.commit()
        conn.close()

        return jsonify({'message': 'Slot creato con successo ✅'}), 200

    except Exception as e:
        return jsonify({'error': f'Errore durante la creazione dello slot: {str(e)}'}), 500


#Prenota uno slot esistente
@api_bp.route('/prenota_slot', methods=['POST'])
def prenota_slot():
    if 'user_id' not in session:
        return jsonify({'error': 'Utente non autenticato'}), 403

    data = request.get_json()
    slot_id = data.get('slot_id')
    utente_id = session['user_id']

    if not slot_id:
        return jsonify({'error': 'ID dello slot mancante'}), 400

    try:
        conn = sqlite3.connect('usersdb.db')
        cur = conn.cursor()

        # Verifica che lo slot esista e sia disponibile
        cur.execute("SELECT * FROM slot WHERE id = ? AND disponibile = 1", (slot_id,))
        slot = cur.fetchone()
        if not slot:
            conn.close()
            return jsonify({'error': 'Slot non disponibile'}), 400

        # Inserisci la prenotazione
        cur.execute("""
            INSERT INTO prenotazione (slot_id, utente_id)
            VALUES (?, ?)
        """, (slot_id, utente_id))

        # Rendi lo slot non più disponibile
        cur.execute("UPDATE slot SET disponibile = 0 WHERE id = ?", (slot_id,))
        conn.commit()
        conn.close()

        return jsonify({'message': 'Prenotazione effettuata con successo'}), 200

    except Exception as e:
        return jsonify({'error': f'Errore nella prenotazione: {e}'}), 500


#Elimina uno slot
@api_bp.route('/slot/<int:slot_id>', methods=['DELETE'])
def delete_slot(slot_id):
    try:
        conn = get_db_connection()
        cur = conn.execute("DELETE FROM slot WHERE id = ?", (slot_id,))
        conn.commit()
        conn.close()
        if cur.rowcount == 0:
            return jsonify({'error': 'Slot non trovato'}), 404
        return jsonify({'message': 'Slot eliminato'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
