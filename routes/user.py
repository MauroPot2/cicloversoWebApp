from flask import Blueprint, render_template, session, redirect, url_for, request, flash
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

    prenotazioni = conn.execute('''
        SELECT p.*, s.Servizio
        FROM prenotazione p
        JOIN servizi s ON p.servizio_id = s.id
        WHERE p.utente_id = ?
        ORDER BY p.data_ora DESC
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
    prenotazioni = conn.execute('''
        SELECT p.*, s.Servizio
        FROM prenotazione p
        JOIN servizi s ON p.servizio_id = s.id
        WHERE p.utente_id = ?
        ORDER BY p.data_ora DESC
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
