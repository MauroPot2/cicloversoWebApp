from flask import Blueprint, jsonify, request, session
from werkzeug.utils import secure_filename
from datetime import datetime
from dateutil.parser import parse
import sqlite3
import os
from slot import Slot

api_bp = Blueprint('api', __name__)
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
    return jsonify([
        {
            'id': s['id'],
            'nome': s['Servizio'],
            'prezzo': s['Prezzo']
            } for s in servizi])

#Recupera slot disponibili
@api_bp.route('/slot', methods=['GET'])
def get_slots():
    start_str = request.args.get('start')
    end_str = request.args.get('end')

    if not start_str or not end_str:
        return jsonify({'error': 'Parametri "start" e "end" mancanti'}), 400

    try:
        start_date = parse(start_str).date()
        end_date = parse(end_str).date()
    except Exception as e:
        return jsonify({'error': f'Formato data non valido: {e}'}), 400

    conn = sqlite3.connect('usersdb.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Estrai slot con join ai servizi
    cur.execute('''
        SELECT sl.id, sl.data, sl.ora_inizio, sl.ora_fine, sl.servizio_id, s.Servizio
        FROM slot sl
        LEFT JOIN servizi s ON sl.servizio_id = s.id
        WHERE sl.data BETWEEN ? AND ? AND sl.disponibile = 1
    ''', (start_date.isoformat(), end_date.isoformat()))

    rows = cur.fetchall()
    conn.close()

    events = []
    for row in rows:
        nome_servizio = row["Servizio"] if row["Servizio"] else f"Slot {row['id']}"
        events.append({
            "id": row["id"],
            "data": row["data"],
            "ora_inizio": row["ora_inizio"],
            "ora_fine": row["ora_fine"],
            "servizio_id": row["servizio_id"],
            "title": nome_servizio
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


#Elimina una prenotazione
@api_bp.route('/prenotazione/<int:id>', methods=['DELETE'])
def delete_prenotazione(id):
    try:
        conn = sqlite3.connect('usersdb.db')
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        # Recupera la prenotazione con info slot
        cur.execute('''
            SELECT p.*, s.data, s.ora_inizio, s.id as slot_id
            FROM prenotazione p
            JOIN slot s ON p.slot_id = s.id
            WHERE p.id = ?
        ''', (id,))
        prenotazione = cur.fetchone()

        # Controllo: prenotazione esistente?
        if not prenotazione:
            return jsonify({"error": "Prenotazione non trovata"}), 404

        # Debug stampa prenotazione
        print("[DEBUG] Prenotazione:", dict(prenotazione))

        # Parsing data e ora con formato corretto
        from datetime import datetime, timedelta
        data_str = prenotazione['data']
        ora_str = prenotazione['ora_inizio']

        try:
            data_ora = datetime.strptime(f"{data_str} {ora_str}", "%Y-%m-%d %H:%M:%S")
        except ValueError as ve:
            print("[ERROR] Errore parsing data/ora:", ve)
            return jsonify({"error": f"Errore nel parsing di data/ora: {ve}"}), 500

        # Controllo annullabilità
        if datetime.now() > data_ora - timedelta(hours=48):
            return jsonify({"error": "Non puoi annullare la prenotazione a meno di 48h dall'appuntamento"}), 400

        cur.execute("DELETE FROM prenotazione WHERE id = ?", (id,))
        cur.execute("UPDATE slot SET disponibile = 1 WHERE id = ?", (prenotazione['slot_id'],))
        conn.commit()
        conn.close()

        print(f"[INFO] Prenotazione {id} annullata e slot {prenotazione['slot_id']} liberato")
        return jsonify({"message": "Prenotazione annullata correttamente."}), 200

    except Exception as e:
        print("[ERROR] Errore durante l'annullamento:", e)
        return jsonify({"error": f"Errore interno del server: {str(e)}"}), 500


@api_bp.route('/prenota_slot_avanzato', methods=['POST'])
def prenota_slot_avanzato():
    if 'user_id' not in session:
        return jsonify({'error': 'Utente non autenticato'}), 403

    utente_id = session['user_id']
    slot_id = request.form.get('slot_id')
    servizio_id = request.form.get('servizio_id')
    messaggio = request.form.get('messaggio', '')

    if not slot_id or not servizio_id:
        return jsonify({'error': 'Dati mancanti per la prenotazione'}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    # Controlla se lo slot è ancora disponibile
    cur.execute("SELECT * FROM slot WHERE id = ? AND disponibile = 1", (slot_id,))
    slot = cur.fetchone()
    if not slot:
        conn.close()
        return jsonify({'error': 'Slot non disponibile'}), 400

    try:
        # Inserisci prenotazione
        cur.execute("""
            INSERT INTO prenotazione (slot_id, utente_id, servizio_id, messaggio)
            VALUES (?, ?, ?, ?)
        """, (slot_id, utente_id, servizio_id, messaggio))
        prenotazione_id = cur.lastrowid

        # Aggiorna disponibilità dello slot
        cur.execute("UPDATE slot SET disponibile = 0 WHERE id = ?", (slot_id,))

        # Salva eventuali immagini
        if 'immagini' in request.files:
            files = request.files.getlist('immagini')
            for file in files:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(UPLOAD_FOLDER, filename)
                    file.save(filepath)
                    cur.execute("""
                        INSERT INTO prenotazione_immagini (prenotazione_id, path)
                        VALUES (?, ?)
                    """, (prenotazione_id, filepath))

        conn.commit()
        return jsonify({'message': 'Prenotazione effettuata con successo!'}), 200

    except Exception as e:
        conn.rollback()
        return jsonify({'error': f"Errore durante la prenotazione: {e}"}), 500
    finally:
        conn.close()
