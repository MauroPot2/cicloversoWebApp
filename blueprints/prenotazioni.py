from flask import Blueprint, render_template, jsonify, request, session, redirect, url_for
import sqlite3
import json

prenotazioni_bp = Blueprint('prenotazioni', __name__)

def salva_slot(slot):
    try:
        connessione = sqlite3.connect('usersdb.db')
        cursore = connessione.cursor()
        cursore.execute('''
            CREATE TABLE IF NOT EXISTS slot (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data TEXT,
                ora_inizio TEXT,
                ora_fine TEXT,
                servizio_id INTEGER,
                disponibile INTEGER NOT NULL DEFAULT 1,
                prenotazioni TEXT,
                FOREIGN KEY (servizio_id) REFERENCES servizio(id)
            )
        ''')
        cursore.execute('''
            INSERT INTO slot (data, ora_inizio, ora_fine, servizio_id, disponibile, prenotazioni)
            VALUES (?, ?, ?, ?, 1, '[]')
        ''', (slot['data'], slot['ora_inizio'], slot['ora_fine'], slot['servizio_id']))
        connessione.commit()
        cursore.close()
        connessione.close()
    except sqlite3.Error as e:
        print(f"Errore nel database: {e}")

def recupera_slot():
    try:
        connessione = sqlite3.connect('usersdb.db')
        cursore = connessione.cursor()
        cursore.execute('SELECT * FROM slot')
        slot_dal_db = cursore.fetchall()
        cursore.close()
        connessione.close()
        slot = []
        for s in slot_dal_db:
            slot.append({
                'id': s[0],
                'data': s[1],
                'ora_inizio': s[2],
                'ora_fine': s[3],
                'servizio_id': s[4],
                'disponibile': s[5],
                'prenotazioni': json.loads(s[6]) if s[6] else []
            })
        return slot
    except sqlite3.Error as e:
        print(f"Errore nel database: {e}")
        return []

@prenotazioni_bp.route('/admin/crea_slot', methods=['POST'])
def crea_slot():
    data = request.get_json()
    slot = {
        'data': data['data'],
        'ora_inizio': data['ora_inizio'],
        'ora_fine': data['ora_fine'],
        'servizio_id': data['servizio']
    }
    salva_slot(slot)
    return '', 204

@prenotazioni_bp.route('/admin/recupera_slot', methods=['GET'])
def get_slot():
    slot = recupera_slot()
    return jsonify(slot)

@prenotazioni_bp.route('/admin/cancella_slot/<int:slot_id>', methods=['DELETE'])
def cancella_slot(slot_id):
    try:
        conn = sqlite3.connect('usersdb.db')
        c = conn.cursor()
        c.execute('DELETE FROM slot WHERE id = ?', (slot_id,))
        conn.commit()
        c.close()
        conn.close()
        return '', 204
    except sqlite3.Error as e:
        print(f"Errore nel database: {e}")
        return '', 500

@prenotazioni_bp.route('/admin/modifica_slot/<int:slot_id>', methods=['PUT'])
def modifica_slot(slot_id):
    data = request.get_json()
    try:
        conn = sqlite3.connect('usersdb.db')
        c = conn.cursor()
        c.execute('UPDATE slot SET data = ?, ora_inizio = ?, ora_fine = ?, servizio_id = ? WHERE id = ?',
                  (data['data'], data['ora_inizio'], data['ora_fine'], data['servizio'], slot_id))
        conn.commit()
        c.close()
        conn.close()
        return '', 204
    except sqlite3.Error as e:
        print(f"Errore nel database: {e}")
        return '', 500

@prenotazioni_bp.route('/admin/aggiungi_prenotazione/<int:slot_id>', methods=['POST'])
def aggiungi_prenotazione(slot_id):
    data = request.get_json()
    try:
        conn = sqlite3.connect('usersdb.db')
        c = conn.cursor()
        c.execute('SELECT prenotazioni FROM slot WHERE id = ?', (slot_id,))
        result = c.fetchone()
        if result and result[0]:
            prenotazioni = json.loads(result[0])
        else:
            prenotazioni = []
        prenotazione = {
            'nome': data['nome'],
            'cognome': data['cognome'],
            'email': data['email'],
            'telefono': data['telefono']
        }
        prenotazioni.append(prenotazione)
        c.execute('UPDATE slot SET prenotazioni = ? WHERE id = ?', (json.dumps(prenotazioni), slot_id))
        conn.commit()
        c.close()
        conn.close()
        return '', 204
    except sqlite3.Error as e:
        print(f"Errore nel database: {e}")
        return '', 500