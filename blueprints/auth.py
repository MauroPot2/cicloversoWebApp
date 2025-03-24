from flask import Blueprint, render_template, request, session, redirect, url_for, flash, jsonify
import sqlite3
import bcrypt
import re
import secrets
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
        password = request.form.get("password") #Aggiunta password
        #aggiungere validazione email e password
        conn = sqlite3.connect('usersdb.db')
        cursore = conn.cursor()
        cursore.execute("SELECT id, hash_password, ruolo FROM utenti WHERE email = ?", (email,))
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

@auth_bp.route('/logout')
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

@auth_bp.route('/reimposta_password', methods=['POST', 'GET'])
def reimposta_password(mail):
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

@auth_bp.route('/reimposta_password/<token>', methods=['POST', 'GET'])
def reimposta_password_token(token, mail):
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