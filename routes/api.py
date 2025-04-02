from flask import Blueprint, jsonify, request
from datetime import datetime
from dateutil.parser import parse
import sqlite3
from slot import Slot

api_bp = Blueprint('api', __name__)

# 📌 Utility: connessione semplice
def get_db_connection():
    conn = sqlite3.connect('usersdb.db')
    conn.row_factory = sqlite3.Row
    return conn

# ✅ Recupera tutti i servizi disponibili
@api_bp.route('/servizi', methods=['GET'])
def get_servizi():
    conn = get_db_connection()
    servizi = conn.execute("SELECT id, Servizio FROM servizi").fetchall()
    conn.close()
    return jsonify([{'id': s['id'], 'nome': s['nome']} for s in servizi])

# ✅ Recupera slot disponibili
@api_bp.route('/slot', methods=['GET'])
def get_slots():
    start_str = request.args.get('start')
    end_str = request.args.get('end')

    if not start_str or not end_str:
        return jsonify({'error': 'Parametri "start" e "end" mancanti'}), 400

    try:
        # Usa parse per supportare timezone e orario
        start_date = parse(start_str).date()
        end_date = parse(end_str).date()
    except Exception as e:
        return jsonify({'error': f'Formato data non valido: {e}'}), 400

    conn = sqlite3.connect('usersdb.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute('''
        SELECT data, ora_inizio, ora_fine, servizio_id
        FROM slot
        WHERE data BETWEEN ? AND ? AND disponibile = 1
    ''', (start_date.isoformat(), end_date.isoformat()))
    rows = cur.fetchall()
    conn.close()

    events = []
    for row in rows:
        events.append({
            "title": f"Servizio {row['servizio_id']}",
            "start": f"{row['data']}T{row['ora_inizio']}",
            "end": f"{row['data']}T{row['ora_fine']}"
        })

    return jsonify(events)

# ✅ Crea uno slot disponibile
@api_bp.route('/slot', methods=['POST'])
def create_slot():
    data = request.get_json()
    try:
        giorno = datetime.strptime(data['data'], '%Y-%m-%d').date()
        ora_inizio = datetime.strptime(data['ora_inizio'], '%H:%M').time()
        ora_fine = datetime.strptime(data['ora_fine'], '%H:%M').time()
        servizio_id = int(data['servizio'])

        conn = get_db_connection()
        conn.execute("""
            INSERT INTO slot (data, ora_inizio, ora_fine, servizio_id, disponibile)
            VALUES (?, ?, ?, ?, 1)
        """, (giorno.isoformat(), ora_inizio.isoformat(), ora_fine.isoformat(), servizio_id))
        conn.commit()
        conn.close()

        return jsonify({'message': 'Slot creato con successo'}), 200
    except Exception as e:
        return jsonify({'error': f'Errore durante la creazione dello slot: {e}'}), 500

# ✅ Prenota uno slot esistente
@api_bp.route('/prenota_slot', methods=['POST'])
def prenota_slot():
    data = request.get_json()
    try:
        giorno = datetime.strptime(data['data'], '%Y-%m-%d').date()
        ora_inizio = datetime.strptime(data['ora_inizio'], '%H:%M').time()
        ora_fine = datetime.strptime(data['ora_fine'], '%H:%M').time()
        servizio_id = int(data['servizio_id'])

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            UPDATE slot
            SET disponibile = 0
            WHERE data = ? AND ora_inizio = ? AND ora_fine = ? AND servizio_id = ? AND disponibile = 1
        """, (
            giorno.isoformat(),
            ora_inizio.isoformat(),
            ora_fine.isoformat(),
            servizio_id
        ))
        if cur.rowcount == 0:
            raise Exception("Nessuno slot disponibile per questi parametri.")
        conn.commit()
        conn.close()

        return jsonify({'message': 'Slot prenotato con successo'}), 200
    except Exception as e:
        return jsonify({'error': f'Errore nella prenotazione: {e}'}), 500

# 🗑️ (Facoltativo) Elimina uno slot
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
