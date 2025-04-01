from flask import Blueprint, jsonify, request
from datetime import datetime
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

# ✅ Recupera slot disponibili per una data
@api_bp.route('/slot', methods=['GET'])
def get_slots():
    data_str = request.args.get('data')
    if not data_str:
        return jsonify({'error': 'Parametro "data" mancante'}), 400
    try:
        data_obj = datetime.strptime(data_str, '%Y-%m-%d').date()
        slots = Slot.get_available_slots_by_date(data_obj)
        return jsonify([{
            'orario': slot.orario.strftime('%H:%M'),
            'servizio_id': slot.servizio_id
        } for slot in slots]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
            INSERT INTO slot (data, orario_inizio, orario_fine, servizio_id, disponibile)
            VALUES (?, ?, ?, 1)
        """, (giorno.isoformat(), ora_inizio.isoformat(), servizio_id))
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
        orario = datetime.strptime(data['orario'], '%H:%M').time()
        servizio_id = int(data['servizio_id'])

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            UPDATE slot
            SET disponibile = 0
            WHERE data = ? AND orario = ? AND servizio_id = ? AND disponibile = 1
        """, (giorno.isoformat(), orario.isoformat(), servizio_id))
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
