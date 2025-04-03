from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from werkzeug.security import check_password_hash, generate_password_hash
from utils.password_utils import hash_password, check_password
import bcrypt
import sqlite3

user_bp = Blueprint('utente', __name__, url_prefix='/utente')

@user_bp.route('/dashboard')
def dashboard_utente():
    if 'user_id' not in session or session.get('ruolo') != 'utente':
        return redirect(url_for('auth.login'))

    user_id = session['user_id']

    conn = sqlite3.connect('usersdb.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    prenotazioni = cur.execute('''
    SELECT 
        p.id AS prenotazione_id,
        s.Servizio,
        s.Prezzo,
        sl.data,
        sl.ora_inizio,
        sl.ora_fine
    FROM prenotazione p
    JOIN slot sl ON p.slot_id = sl.id
    JOIN servizi s ON sl.servizio_id = s.id
    WHERE p.utente_id = ?
    ORDER BY sl.data DESC, sl.ora_inizio
''', (user_id,)).fetchall()

    utente = cur.execute('SELECT * FROM utenti WHERE id = ?', (user_id,)).fetchone()
    conn.close()

    return render_template('utente/dashboard.html', prenotazioni=prenotazioni, utente=utente)

@user_bp.route('/prenotazioni')
def visualizza_prenotazioni():
    if 'user_id' not in session or session.get('ruolo') != 'utente':
        return redirect(url_for('auth.login'))

    user_id = session['user_id']

    conn = sqlite3.connect('usersdb.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    prenotazioni = cur.execute('''
        SELECT 
        p.id AS prenotazione_id,
        s.Servizio,
        s.Prezzo,
        sl.data,
        sl.ora_inizio,
        sl.ora_fine
    FROM prenotazione p
    JOIN slot sl ON p.slot_id = sl.id
    JOIN servizi s ON sl.servizio_id = s.id
    WHERE p.utente_id = ?
    ORDER BY sl.data DESC, sl.ora_inizio
    ''', (user_id,)).fetchall()

    conn.close()
    return render_template('utente/prenotazioni_utente.html', prenotazioni=prenotazioni)

@user_bp.route('/profilo', methods=['GET', 'POST'])
def profilo():
    if 'user_id' not in session or session.get('ruolo') != 'utente':
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    conn = sqlite3.connect('usersdb.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    if request.method == 'POST':
        nome = request.form['nome']
        cognome = request.form['cognome']
        email = request.form['email']
        cellulare = request.form['cellulare']

        cur.execute('''
            UPDATE utenti
            SET nome = ?, cognome = ?, email = ?, cellulare = ?
            WHERE id = ?
        ''', (nome, cognome, email, cellulare, user_id))
        conn.commit()
        conn.close()
        flash("Dati aggiornati con successo ✅", "success")
        return redirect(url_for('utente.profilo'))

    utente = cur.execute("SELECT * FROM utenti WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return render_template('utente/profilo.html', utente=utente)

@user_bp.route('/calendario')
def calendario():
    if 'user_id' not in session or session.get('ruolo') != 'utente':
        return redirect(url_for('auth.login'))
    return render_template('utente/calendario.html')
###Cambia Password
@user_bp.route('/cambia_password', methods=['POST'])
def cambia_password():
    if 'user_id' not in session or session.get('ruolo') != 'utente':
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    vecchia_password = request.form['vecchia_password']
    nuova_password = request.form['nuova_password']
    conferma_password = request.form['conferma_password']

    if nuova_password != conferma_password:
        flash("Le nuove password non coincidono.", "danger")
        return redirect(url_for('utente.profilo'))

    conn = sqlite3.connect('usersdb.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("SELECT hash_password FROM utenti WHERE id = ?", (user_id,))
    user = cur.fetchone()

    if not user:
        conn.close()
        flash("Utente non trovato.", "danger")
        return redirect(url_for('utente.profilo'))

    # ✅ Verifica la password corrente usando la funzione centralizzata
    if not check_password(vecchia_password, user['hash_password']):
        conn.close()
        flash("La password attuale non è corretta.", "danger")
        return redirect(url_for('utente.profilo'))

    # ✅ Hash della nuova password
    nuova_hash = hash_password(nuova_password)

    cur.execute("UPDATE utenti SET hash_password = ? WHERE id = ?", (nuova_hash, user_id))
    conn.commit()
    conn.close()

    flash("Password aggiornata con successo!", "success")
    return redirect(url_for('utente.profilo'))