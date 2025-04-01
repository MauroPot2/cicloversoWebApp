from flask import Blueprint, render_template, jsonify, request, session, flash
from .auth import admin_required
from slot import Slot
import sqlite3
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/', methods=['GET'])
@admin_required
def admin():
    conn = sqlite3.connect('usersdb.db')
    cursore = conn.cursor()
    cursore.execute("SELECT * FROM utenti WHERE id = ?", (session['user_id'],))
    admin_utente = cursore.fetchone()
    conn.close()
    return render_template("admin/admin_index.html", admin_utente=admin_utente)

@admin_bp.route('/aggiungi_slot', methods=['POST'])
@admin_required
def aggiungi_slot():
    if request.method == 'POST':
        data = request.form.get('data')
        orario = request.form.get('orario')
        servizio_id = request.form.get('servizio_id')

        try:
            data_datetime = datetime.strptime(data, '%Y-%m-%d').date()
            orario_time = datetime.strptime(orario, '%H:%M').time()

            slot = Slot(data_datetime, orario_time, servizio_id=servizio_id)
            slot.save()

            return jsonify({"messaggio": "Slot aggiunto con successo."})
        except ValueError:
            return jsonify({"error": "Formato data o orario non valido."}), 400
        except sqlite3.Error as e:
            return jsonify({"error": f"Errore del database: {e}"}), 500
        except Exception as e:
            print(f"Errore imprevisto: {e}")
            return jsonify({"error": f"Errore imprevisto: {e}"}), 500

@admin_bp.route('/slot_disponibili', methods=['GET'])
@admin_required
def admin_slot_disponibili():
    data = session.get('data_slot')
    session.pop('data_slot', None)

    if not data:
        flash('Data non specificata.', 'danger')
        return render_template('admin/slot_disponibili.html', data=None, slot_disponibili=[])

    try:
        data_datetime = datetime.strptime(data, '%Y-%m-%d').date()
        slot_disponibili = Slot.get_slots_by_date(data_datetime)
    except ValueError:
        flash('Formato data non valido.', 'danger')
        slot_disponibili = []
    except sqlite3.Error as e:
        flash(f'Errore del database: {e}', 'danger')
        slot_disponibili = []
    except Exception as e:
        print(f"Errore imprevisto: {e}")
        flash(f'Errore imprevisto: {e}', 'danger')
        slot_disponibili = []

    return render_template('admin/slot_disponibili.html', data=data, slot_disponibili=slot_disponibili)

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
