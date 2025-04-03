from flask import Blueprint, render_template, request, session, redirect, url_for, flash, jsonify, render_template_string
from utils.email_utils import invia_mail_benvenuto
from extension import mail
import sqlite3
import bcrypt
import re
import os
import secrets
from werkzeug.utils import secure_filename
from flask_mail import Message


auth_bp = Blueprint('auth', __name__)

def admin_required(f):
    def decorated_function(*args, **kwargs):
        if not session.get('ruolo') or (session.get('ruolo') != 'admin' and session.get('ruolo') != 'root'):
            return jsonify({"error": "Accesso non autorizzato"}), 403
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@auth_bp.route('/log_in', methods=['POST', 'GET'])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        conn = sqlite3.connect('usersdb.db')
        cursore = conn.cursor()
        cursore.execute("SELECT id, hash_password, ruolo FROM utenti WHERE email = ?", (email,))
        user = cursore.fetchone()
        conn.close()
        if user:
            if check_password(password, user[1]):
                session["user_id"] = user[0]
                session["ruolo"] = user[2]
                if user[2] == 'admin':
                    return redirect(url_for('admin.admin'))  # Reindirizza all'admin page
                else:
                    return redirect(url_for('utente.dashboard_utente'))  # Reindirizza alla pagina di login per gli utenti normali
            else:
                return render_template("categoria/login.html", error="password errata")
        else:
            return render_template("categoria/login.html", error="email non trovata")
    return render_template("categoria/login.html")

@auth_bp.route('/logout')
def logout():
    session.pop("user_id", None)
    return redirect(url_for('index'))

def hash_password(password: str) -> str:
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8')

def check_password(password: str, hashed_password: str) -> bool:
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password)

def is_strong_password(password):
    if len(password) < 8:
        return False
    if not re.search(r'[.!@#$%^&*]', password):
        return False
    return True

@auth_bp.route('/registrati', methods=['POST', 'GET'])
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
            cursore.execute(
                "INSERT INTO utenti (nome, cognome, email, cellulare, hash_password) VALUES (?, ?, ?, ?, ?)",
                (nome, cognome, email, cellulare, hashed_password)
            )
            conn.commit()

            # ✉️ Invia la mail di benvenuto
            try:
                invia_mail_benvenuto(email, nome)
            except Exception as e:
                print(f"Errore nell'invio della mail di benvenuto: {e}")

            flash('Registrazione avvenuta con successo. Effettua il login.', 'success')
            return redirect(url_for('auth.login'))
            
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

@auth_bp.route('/reimposta_password', methods=['GET', 'POST'])
def reimposta_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()

        if not email:
            flash("Inserisci un'email valida.", "danger")
            return render_template('categoria/reimposta_password.html')

        conn = sqlite3.connect('usersdb.db')
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        cur.execute("SELECT id FROM utenti WHERE email = ?", (email,))
        user = cur.fetchone()

        if not user:
            flash("Nessun utente trovato con questa email.", "danger")
            conn.close()
            return render_template('categoria/reimposta_password.html')

        #Genera token sicuro e salva nel DB
        token = secrets.token_urlsafe(32)
        cur.execute("UPDATE utenti SET reset_token = ? WHERE id = ?", (token, user['id']))
        conn.commit()
        conn.close()

        #Link per reimpostare la password
        reset_link = url_for('auth.reimposta_password', token=token, _external=True)

        #Invia email con il link di reset
        try:
            msg = Message(
                subject="Reimposta la tua password - CicloVerso",
                sender="noreply@cicloverso.com",
                recipients=[email]
            )
            msg.body = f"""
Hai richiesto la reimpostazione della password per il tuo account CicloVerso.

Clicca il link qui sotto per reimpostarla:

{reset_link}

Se non hai richiesto questa operazione, ignora semplicemente questa email.
            """.strip()
            mail.send(msg)
            flash("Email inviata! Controlla la tua casella di posta. 📬", "success")
        except Exception as e:
            flash("Errore durante l'invio dell'email. Riprova più tardi.", "danger")
            print(f"Errore invio email reset: {e}")

    return render_template("categoria/reimposta_password.html")