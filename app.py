from flask import Flask, render_template, jsonify, request, session, redirect, url_for, flash
from flask_session import Session
from slot import Slot
import sqlite3
from datetime import datetime, timedelta
import hashlib
import bcrypt
import re
import secrets
from flask_mail import Mail, Message
import os
import config

secret_key = secrets.token_hex(16)
print(f"Chiave segreta: {secret_key}")

app = Flask(__name__)
app.secret_key = secret_key
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Configurazione Flask-Mail
app.config['MAIL_SERVER'] = config.MAIL_SERVER
app.config['MAIL_PORT'] = config.MAIL_PORT
app.config['MAIL_USE_TLS'] = config.MAIL_USE_TLS
app.config['MAIL_USERNAME'] = config.MAIL_USERNAME
app.config['MAIL_PASSWORD'] = config.MAIL_PASSWORD
mail = Mail(app)

def admin_required(f):
    def decorated_function(*args, **kwargs):
        if not session.get('ruolo') or (session.get('ruolo') != 'admin' and session.get('ruolo') != 'root'):
            return jsonify({"error": "Accesso non autorizzato"}), 403
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@app.route('/admin', methods=['GET'])
@admin_required
def admin():
    """Route per la pagina admin."""
    return render_template("admin/admin_index.html")


@app.route('/admin/aggiungi_slot', methods=['POST'])
@admin_required
def aggiungi_slot():
    if request.method == 'POST':
        data = request.form.get('data')
        orario = request.form.get('orario')
        servizio_id = request.form.get('servizio_id') #recupera il servizio

        try:
            data_datetime = datetime.strptime(data, '%Y-%m-%d').date()
            orario_time = datetime.strptime(orario, '%H:%M').time()

            slot = Slot(data_datetime, orario_time, servizio_id=servizio_id) #passa il servizio
            slot.save()

            flash('Slot aggiunto con successo.', 'success')
        except ValueError:
            flash('Formato data o orario non valido.', 'danger')
        except sqlite3.Error as e:
            flash(f'Errore del database: {e}', 'danger')
        except Exception as e:
            print(f"Errore imprevisto: {e}")
            flash(f'Errore imprevisto: {e}', 'danger')
        finally:
            session['data_slot'] = data
            return redirect(url_for('admin_slot_disponibili'))

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

@app.route('/admin/slot_disponibili', methods=['GET'])
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
    
@app.route('/slot_prenotazione', methods=['GET'])
def slot_prenotazione():
    data_str = request.args.get('data')
    if not data_str:
        return jsonify({"error": "Data mancante"}), 400

    try:
        data_datetime = datetime.strptime(data_str, '%Y-%m-%d').date()
        slot_disponibili = Slot.get_available_slots_by_date(data_datetime)
        slot_dati = [{'orario': slot.orario.strftime('%H:%M'), 'servizio_id': slot.servizio_id} for slot in slot_disponibili]  # Restituisce orario e servizio
        return jsonify(slot_dati)
    except ValueError:
        return jsonify({"error": "Formato data non valido"}), 400

@app.route('/admin/servizi', methods=['GET'])
@admin_required
def gestisci_servizi():
    conn = sqlite3.connect('usersdb.db')
    conn.row_factory = sqlite3.Row
    servizi = conn.execute("SELECT * FROM servizi").fetchall()
    conn.close()
    return render_template('admin/servizi.html', servizi=servizi)

@app.route('/admin/prenotazioni', methods=['GET'])
@admin_required
def gestisci_prenotazioni():
    conn = sqlite3.connect('usersdb.db')
    conn.row_factory = sqlite3.Row
    prenotazioni = conn.execute("SELECT * FROM prenotazioni").fetchall()
    conn.close()
    return render_template('admin/prenotazioni.html', prenotazioni=prenotazioni)

@app.route('/admin/utenti', methods=['GET'])
@admin_required
def gestisci_utenti():
    conn = sqlite3.connect('usersdb.db')
    conn.row_factory = sqlite3.Row
    utenti = conn.execute("SELECT * FROM utenti").fetchall()
    conn.close()
    return render_template('admin/utenti.html', utenti=utenti)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/contatti')
def contatti():
    return render_template("categoria/contatti.html")

@app.route('/manutenzione')
def manutenzione():
    conn = sqlite3.connect('usersdb.db')
    conn.row_factory = sqlite3.Row
    servizi = conn.execute("SELECT * FROM servizi").fetchall()
    conn.close()
    return render_template("categoria/manutenzione.html", servizi=servizi)

@app.route('/biomeccanica')
def biomeccanica():
    return render_template("categoria/biomeccanica.html")


@app.route('/prenota', methods=['POST', 'GET'])
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

@app.route('/log_in',methods=['POST','GET'])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password") #Aggiunta password
        #aggiungere validazione email e password
        conn = sqlite3.connect('usersdb.db')
        cursore = conn.cursor()
        cursore.execute("SELECT id, hash_password, ruolo FROM utenti WHERE email = ?", (email,)) #aggiunta hash_password
        user = cursore.fetchone()
        conn.close()
        if user:
            if check_password(password, user[1]): #aggiunta controllo password
                session["user_id"] = user[0]
                session["ruolo"] = user[2]
                return redirect(url_for("index"))
            else:
                return render_template("categoria/login.html", error = "password errata")
        else:
            return render_template("categoria/login.html", error = "email non trovata")

    return render_template("categoria/login.html")

@app.route('/logout')
def logout():
    session.pop("user_id", None)
    return redirect(url_for('index'))

def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password

def check_password(password, hashed_password):
     return bcrypt.checkpw(password.encode('utf-8'), hashed_password)

def is_strong_password(password):
    if len(password) < 8:
        return False
    if not re.search(r'[!@#$%^&*]', password):
        return False
    return True

@app.route('/registrati', methods=['POST', 'GET'])
def registrati():
    if request.method == 'POST':
        nome = request.form.get('nome').strip()
        cognome = request.form.get('cognome').strip()
        email = request.form.get('email').strip()
        cellulare = request.form.get('cellulare').strip()
        password = request.form.get('password')

        # Validazione dei campi obbligatori
        if not nome or not cognome or not email or not cellulare or not password:
            flash('Tutti i campi sono obbligatori.', 'danger')
            return render_template('categoria/registrazione.html', nome=nome, cognome=cognome, email=email, cellulare=cellulare)

        # Validazione della lunghezza massima
        if len(nome) > 100 or len(cognome) > 100 or len(email) > 100 or len(cellulare) > 15:
            flash('Uno o più campi superano la lunghezza massima consentita.', 'danger')
            return render_template('categoria/registrazione.html', nome=nome, cognome=cognome, email=email, cellulare=cellulare)

        # Validazione del formato email
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash('Formato email non valido.', 'danger')
            return render_template('categoria/registrazione.html', nome=nome, cognome=cognome, email=email, cellulare=cellulare)

        # Validazione del formato cellulare (esempio: solo numeri e '+')
        if not re.match(r"^[0-9\+]+$", cellulare):
            flash('Formato cellulare non valido.', 'danger')
            return render_template('categoria/registrazione.html', nome=nome, cognome=cognome, email=email, cellulare=cellulare)

        # Validazione della password
        if not is_strong_password(password):
            flash('Password non valida. Deve contenere almeno 8 caratteri e un carattere speciale.', 'danger')
            return render_template('categoria/registrazione.html', nome=nome, cognome=cognome, email=email, cellulare=cellulare)

        try:
            conn = sqlite3.connect('usersdb.db')
            cursore = conn.cursor()

            # Verifica email esistente
            cursore.execute("SELECT id FROM utenti WHERE email = ?", (email,))
            if cursore.fetchone():
                flash('Email già registrata.', 'danger')
                return render_template('categoria/registrazione.html', nome=nome, cognome=cognome, email=email, cellulare=cellulare)

            # Verifica cellulare esistente
            cursore.execute("SELECT id FROM utenti WHERE cellulare = ?", (cellulare,))
            if cursore.fetchone():
                flash('Cellulare già registrato.', 'danger')
                return render_template('categoria/registrazione.html', nome=nome, cognome=cognome, email=email, cellulare=cellulare)

            # Inserisci il nuovo utente con password hashata
            hashed_password = hash_password(password)
            cursore.execute("INSERT INTO utenti (nome, cognome, email, cellulare, hash_password) VALUES (?, ?, ?, ?, ?)", (nome, cognome, email, cellulare, hashed_password))
            conn.commit()
            print(f"Righe inserite: {cursore.rowcount}")
            print(f"Ultimo ID inserito: {cursore.lastrowid}")
            flash('Registrazione avvenuta con successo. Effettua il login.', 'success')
            return redirect(url_for('login'))

        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed: utenti.email" in str(e):
                flash("Email già registrata.", "danger")
            elif "UNIQUE constraint failed: utenti.cellulare" in str(e):
                flash("Cellulare già registrato.", "danger")
            else:
                flash(f"Errore di integrità del database: {e}", "danger")
            return render_template("categoria/registrazione.html", nome=nome, cognome=cognome, email=email, cellulare=cellulare)

        except sqlite3.Error as e:
            print(f"Errore del database: {e}")
            flash(f'Errore del database: {e}', 'danger')
            return render_template('categoria/registrazione.html', nome=nome, cognome=cognome, email=email, cellulare=cellulare)

        except Exception as e:
            print(f"Errore imprevisto: {e}")
            flash(f'Errore imprevisto: {e}', 'danger')
            return render_template('categoria/registrazione.html', nome=nome, cognome=cognome, email=email, cellulare=cellulare)

        finally:
            if 'conn' in locals():
                conn.close()

    return render_template('categoria/registrazione.html')

@app.route('/reimposta_password', methods=['POST', 'GET'])
def reimposta_password():
    if request.method == 'POST':
        email = request.form.get('email')
        conn = sqlite3.connect('usersdb.db')
        cursore = conn.cursor()
        cursore.execute("SELECT id FROM utenti WHERE email = ?", (email,))
        user = cursore.fetchone()
        if user:
            token = secrets.token_urlsafe(16)
            cursore.execute("UPDATE utenti SET reset_token = ? WHERE id = ?", (token, user[0]))
            conn.commit()
            conn.close()
            msg = Message('Reimposta la tua password', sender='your_email@example.com', recipients=[email])
            msg.body = f'Clicca sul seguente link per reimpostare la tua password: {url_for("reimposta_password_token", token=token, _external=True)}'
            mail.send(msg)
            flash('Ti è stata inviata un\'email con le istruzioni per reimpostare la password.', 'info')
            return redirect(url_for('login'))
        else:
            flash('Email non trovata.', 'danger')
    return render_template('categoria/reimposta_password.html')

@app.route('/reimposta_password/<token>', methods=['POST', 'GET'])
def reimposta_password_token(token):
    conn = sqlite3.connect('usersdb.db')
    cursore = conn.cursor()
    cursore.execute("SELECT id FROM utenti WHERE reset_token = ?", (token,))
    user = cursore.fetchone()
    if not user:
        flash('Token non valido.', 'danger')
        return redirect(url_for('login'))
    if request.method == 'POST':
        password = request.form.get('password')
        if not is_strong_password(password):
            flash('Password non valida.', 'danger')
            return render_template('categoria/reimposta_password_token.html', token=token)
        hashed_password = hash_password(password)
        cursore.execute("UPDATE utenti SET password = ?, reset_token = NULL WHERE id = ?", (hashed_password, user[0]))
        conn.commit()
        conn.close()
        flash('Password reimpostata con successo.', 'success')
        return redirect(url_for('login'))
    return render_template('categoria/reimposta_password_token.html', token=token)

if __name__ == '__main__':
    app.run(debug=True)