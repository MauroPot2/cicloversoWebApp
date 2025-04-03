from flask import Blueprint, render_template, jsonify, request, session, flash, redirect, url_for
from .auth import admin_required
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from slot import Slot
from generaSlotAuto import genera_slot_per_data
from utils.email_utils import invia_mail_benvenuto
import sqlite3
import os
from datetime import datetime, time

UPLOAD_FOLDER = 'static/img'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    


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
###GESTIONE PRENOTAZIONI
@admin_bp.route('/prenotazioni', methods=['GET'])
@admin_required
def gestisci_prenotazioni():
    conn = sqlite3.connect('usersdb.db')
    conn.row_factory = sqlite3.Row
    prenotazioni = conn.execute('''
        SELECT 
            p.id AS prenotazione_id,
            u.nome, u.cognome, u.email,
            s.Servizio,
            sl.data, sl.ora_inizio, sl.ora_fine
        FROM prenotazione p
        JOIN utenti u ON p.utente_id = u.id
        JOIN slot sl ON p.slot_id = sl.id
        JOIN servizi s ON sl.servizio_id = s.id
        ORDER BY sl.data DESC, sl.ora_inizio
    ''').fetchall()
    conn.close()
    return render_template('admin/prenotazioni.html', prenotazioni=prenotazioni)
    

###GESTIONE UTENTI
@admin_bp.route('/utenti', methods=['GET'])
@admin_required
def gestisci_utenti():
    search = request.args.get('search', '').strip()

    conn = sqlite3.connect('usersdb.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    if search:
        query = """
            SELECT * FROM utenti
            WHERE nome LIKE ? OR cognome LIKE ? OR email LIKE ?
        """
        like = f"%{search}%"
        utenti = cur.execute(query, (like, like, like)).fetchall()
    else:
        utenti = cur.execute("SELECT * FROM utenti").fetchall()

    conn.close()
    return render_template('admin/utenti.html', utenti=utenti, search=search)

@admin_bp.route('/aggiungi_utente', methods=['GET', 'POST'])
@admin_required
def aggiungi_utente():
    if request.method == 'POST':
        nome = request.form['nome']
        cognome = request.form['cognome']
        email = request.form['email']
        cellulare = request.form['cellulare']
        ruolo = request.form['ruolo']
        password = request.form['password']

        hash_password = generate_password_hash(password)

        conn = sqlite3.connect('usersdb.db')
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO utenti (nome, cognome, email, cellulare, ruolo, hash_password)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (nome, cognome, email, cellulare, ruolo, hash_password))
        conn.commit()
        conn.close()
        try:
            invia_mail_benvenuto(email, nome)
        except Exception as e:
            print(f"Errore nell'invio dell'email: {e}")
        flash("Utente aggiunto con successo!", "success")
        return redirect(url_for('admin.gestisci_utenti'))

    return render_template("admin/aggiungi_utente.html")

@admin_bp.route('/utenti/modifica/<int:id>', methods=['GET', 'POST'])
@admin_required
def modifica_utente(id):
    conn = sqlite3.connect('usersdb.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    if request.method == 'POST':
        nome = request.form['nome']
        cognome = request.form['cognome']
        email = request.form['email']
        cellulare = request.form['cellulare']
        ruolo = request.form['ruolo']
        cur.execute('''
            UPDATE utenti
            SET nome = ?, cognome = ?, email = ?, cellulare = ?, ruolo = ?
            WHERE id = ?
        ''', (nome, cognome, email, cellulare, ruolo, id))
        conn.commit()
        conn.close()
        flash("Utente aggiornato con successo", "success")
        return redirect(url_for('admin.gestisci_utenti'))

    cur.execute("SELECT * FROM utenti WHERE id = ?", (id,))
    utente = cur.fetchone()
    conn.close()
    return render_template('admin/modifica_utente.html', utente=utente)

@admin_bp.route('/utenti/elimina/<int:id>', methods=['POST'])
@admin_required
def elimina_utente(id):
    conn = sqlite3.connect('usersdb.db')
    cur = conn.cursor()
    cur.execute("DELETE FROM utenti WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash("Utente eliminato con successo", "success")
    return redirect(url_for('admin.gestisci_utenti'))



###GESTISCI SERVIZI
@admin_bp.route('/servizi', methods=['GET'])
@admin_required
def gestisci_servizi():
    conn = sqlite3.connect('usersdb.db')
    conn.row_factory = sqlite3.Row
    servizi = conn.execute("SELECT * FROM servizi").fetchall()
    conn.close()
    return render_template('admin/servizi.html', servizi=servizi)

@admin_bp.route('/servizi/aggiungi', methods=['GET', 'POST'])
@admin_required
def aggiungi_servizio():
    if request.method == 'POST':
        nome = request.form['nome']
        prezzo = request.form['prezzo']
        disponibilita = request.form['disponibilita']
        file = request.files['immagine']

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
        else:
            filename = "default.png"

        conn = sqlite3.connect('usersdb.db')
        conn.execute('INSERT INTO servizi (Servizio, Prezzo, Disponibilitá, immagine) VALUES (?, ?, ?, ?)', 
                    (nome, prezzo, disponibilita, f"{UPLOAD_FOLDER}/{filename}"))
        conn.commit()
        conn.close()
        flash("Servizio aggiunto con successo", "success")
        return redirect(url_for('admin.gestisci_servizi'))

    # GET → mostra il form vuoto
    return render_template('admin/servizi_form.html', servizio=None)

@admin_bp.route('/servizi/modifica/<int:servizio_id>', methods=['GET', 'POST'])
@admin_required
def modifica_servizio(servizio_id):
    conn = sqlite3.connect('usersdb.db')
    conn.row_factory = sqlite3.Row
    servizio = conn.execute("SELECT * FROM servizi WHERE id = ?", (servizio_id,)).fetchone()

    if request.method == 'POST':
        nome = request.form['nome']
        prezzo = request.form['prezzo']
        disponibilita = request.form['disponibilita']

        # Gestione immagine
        file = request.files.get('immagine')
        if file and file.filename != '' and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            immagine_path = f"{UPLOAD_FOLDER}/{filename}"
        else:
            # Nessuna nuova immagine -> mantieni quella esistente
            immagine_path = servizio['immagine']

        # Update query
        conn.execute("""
            UPDATE servizi SET Servizio = ?, Prezzo = ?, Disponibilitá = ?, immagine = ?
            WHERE id = ?
        """, (nome, prezzo, disponibilita, immagine_path, servizio_id))
        conn.commit()
        conn.close()

        flash('Servizio aggiornato con successo', 'success')
        return redirect(url_for('admin.gestisci_servizi'))

    conn.close()
    return render_template('admin/servizi_form.html', servizio=servizio)

@admin_bp.route('/servizi/elimina/<int:servizio_id>', methods=['POST'])
@admin_required
def elimina_servizio(servizio_id):
    conn = sqlite3.connect('usersdb.db')
    conn.execute("DELETE FROM servizi WHERE id = ?", (servizio_id,))
    conn.commit()
    conn.close()
    flash('Servizio eliminato con successo', 'success')
    return redirect(url_for('admin.gestisci_servizi'))


###SLOT AUTOMATICI
@admin_bp.route('/genera_slot_auto', methods=['POST'])
@admin_required
def genera_slot_auto():
    data = request.json.get('data')  #il formato che legge date é: '2025-04-03'
    try:
        giorno = datetime.strptime(data, '%Y-%m-%d').date()
        genera_slot_per_data(giorno)
        return jsonify({'message': 'Slot generati automaticamente'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
###ORARI APERTURA
@admin_bp.route('/orari_apertura', methods=['GET'])
@admin_required
def mostra_orari_apertura():
    conn = sqlite3.connect('usersdb.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM orari_apertura LIMIT 1")
    orari = cur.fetchone()
    conn.close()
    return render_template('admin/orari_apertura.html', orari=orari)

@admin_bp.route('/orari_apertura', methods=['POST'])
@admin_required
def salva_orari_apertura():
    dati = request.form
    conn = sqlite3.connect('usersdb.db')
    cur = conn.cursor()

    cur.execute('''
        UPDATE orari_apertura
        SET apertura_mattina = ?, chiusura_mattina = ?, apertura_pomeriggio = ?, chiusura_pomeriggio = ?, durata_slot = ?
        WHERE id = 1
    ''', (
        dati['apertura_mattina'],
        dati['chiusura_mattina'],
        dati['apertura_pomeriggio'],
        dati['chiusura_pomeriggio'],
        int(dati['durata_slot'])
    ))

    conn.commit()
    conn.close()

    flash("Orari aggiornati con successo!", "success")
    return redirect('/admin/orari_apertura')


@admin_bp.route('/prenotazioni/modifica/<int:prenotazione_id>', methods=['GET', 'POST'])
@admin_required
def modifica_prenotazione(prenotazione_id):
    conn = sqlite3.connect('usersdb.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    if request.method == 'POST':
        nuova_data = request.form['data_ora']
        nuovo_servizio_id = request.form['servizio_id']

        cur.execute("""
            UPDATE prenotazione
            SET data_ora = ?, servizio_id = ?
            WHERE id = ?
        """, (nuova_data, nuovo_servizio_id, prenotazione_id))

        conn.commit()

        # Recupera info per email
        cur.execute("""
            SELECT u.email, u.nome FROM prenotazione p
            JOIN utenti u ON p.utente_id = u.id
            WHERE p.id = ?
        """, (prenotazione_id,))
        utente = cur.fetchone()
        conn.close()

        try:
            from utils.email_utils import invia_mail_modifica_prenotazione
            invia_mail_modifica_prenotazione(utente['email'], utente['nome'], nuova_data)
        except Exception as e:
            print(f"Errore nell'invio della mail di modifica: {e}")

        flash("Prenotazione aggiornata!", "success")
        return redirect(url_for('admin.gestisci_prenotazioni'))

    # GET -> visualizza prenotazione
    cur.execute("SELECT * FROM prenotazione WHERE id = ?", (prenotazione_id,))
    prenotazione = cur.fetchone()

    servizi = cur.execute("SELECT * FROM servizi").fetchall()
    conn.close()
    return render_template('admin/modifica_prenotazione.html', prenotazione=prenotazione, servizi=servizi)

@admin_bp.route('/prenotazioni/elimina/<int:prenotazione_id>', methods=['POST'])
@admin_required
def elimina_prenotazione(prenotazione_id):
    conn = sqlite3.connect('usersdb.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Recupera info utente
    cur.execute("""
        SELECT u.email, u.nome, p.data_ora
        FROM prenotazione p
        JOIN utenti u ON p.utente_id = u.id
        WHERE p.id = ?
    """, (prenotazione_id,))
    prenotazione = cur.fetchone()

    cur.execute("DELETE FROM prenotazione WHERE id = ?", (prenotazione_id,))
    conn.commit()
    conn.close()

    try:
        from utils.email_utils import invia_mail_annullamento
        invia_mail_annullamento(prenotazione['email'], prenotazione['nome'], prenotazione['data_ora'])
    except Exception as e:
        print(f"Errore nell'invio della mail di annullamento: {e}")

    flash("Prenotazione annullata", "warning")
    return redirect(url_for('admin.gestisci_prenotazioni'))
