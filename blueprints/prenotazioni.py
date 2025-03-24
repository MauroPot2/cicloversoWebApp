from flask import Blueprint, render_template, jsonify, request, session, redirect, url_for
import sqlite3
from datetime import datetime, timedelta
from slot import Slot  # Assicurati che slot.py sia nel percorso corretto

prenotazioni_bp = Blueprint('prenotazioni', __name__)

def genera_slot_prenotazione(orari_apertura, data_selezionata, durata_slot_minuti=30):
    """
    Genera una lista di slot di prenotazione basati sugli orari di apertura del negozio e la data selezionata.
    """
    slot_prenotazione = []
    for inizio_orario, fine_orario in orari_apertura:
        inizio = datetime(data_selezionata.year, data_selezionata.month, data_selezionata.day, inizio_orario.hour, inizio_orario.minute)
        fine = datetime(data_selezionata.year, data_selezionata.month, data_selezionata.day, fine_orario.hour, fine_orario.minute)
        ora_corrente = inizio
        while ora_corrente < fine:
            slot_prenotazione.append(ora_corrente.strftime("%H:%M"))
            ora_corrente = ora_corrente + timedelta(minutes=durata_slot_minuti)
    return slot_prenotazione

@prenotazioni_bp.route('/slot_prenotazione', methods=['GET'])
def slot_prenotazione():
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

@prenotazioni_bp.route('/prenota', methods=['POST', 'GET'])
def prenota():
    """Gestisce le prenotazioni dei servizi."""
    if not session.get('user_id'):
        return redirect(url_for('login'))

    conn = sqlite3.connect('usersdb.db')
    conn.row_factory = sqlite3.Row
    servizi = conn.execute('SELECT * FROM servizi').fetchall()
    conn.close()

    if request.method == 'GET':
        return render_template("categoria/prenotazione.html", servizi=servizi)

    elif request.method == 'POST':
        dati_prenotazione = request.get_json()

        if not dati_prenotazione or 'data' not in dati_prenotazione or 'orario' not in dati_prenotazione or 'servizio_id' not in dati_prenotazione:
            return jsonify({"error": "Dati mancanti"}), 400

        try:
            data_selezionata = datetime.strptime(dati_prenotazione['data'], '%Y-%m-%d')
            orario_selezionato = dati_prenotazione['orario']
            servizio_id = dati_prenotazione['servizio_id']
        except ValueError:
            return jsonify({"error": "Formato data o orario non valido"}), 400

        try:
            conn = sqlite3.connect('usersdb.db')
            cursore = conn.cursor()

            # Inizio della transazione
            cursore.execute("BEGIN TRANSACTION")

            # Verifica la disponibilità dello slot
            cursore.execute("SELECT disponibile FROM slot_disponibili WHERE data = ? AND orario = ?", (data_selezionata.strftime('%Y-%m-%d'), orario_selezionato))
            slot = cursore.fetchone()
            if not slot or slot[0] != 1:
                conn.close()
                return jsonify({"error": "Slot non disponibile"}), 400

            # Verifica che il servizio esista
            cursore.execute("SELECT ServiziID FROM servizi WHERE ServiziID = ?", (servizio_id,))
            servizio = cursore.fetchone()
            if not servizio:
                conn.close()
                return jsonify({"error": "Servizio non trovato"}), 400

            # Memorizza la prenotazione
            cursore.execute("INSERT INTO prenotazioni (data_ora, servizio_id, utente_id) VALUES (?, ?, ?)", (datetime.combine(data_selezionata, datetime.strptime(orario_selezionato, '%H:%M').time()), servizio_id, session["user_id"]))

            # Aggiorna la disponibilità dello slot
            cursore.execute("UPDATE slot_disponibili SET disponibile = 0 WHERE data = ? AND orario = ?", (data_selezionata.strftime('%Y-%m-%d'), orario_selezionato))

            # Commit della transazione
            conn.commit()
            conn.close()

            return jsonify({'messaggio': 'Prenotazione effettuata con successo!'}), 201

        except sqlite3.Error as e:
            # Rollback della transazione in caso di errore
            conn.rollback()
            conn.close()
            return jsonify({"error": f"Errore del database: {e}"}), 500
        except Exception as e:
            return jsonify({"error": f"Errore generico: {e}"}), 500