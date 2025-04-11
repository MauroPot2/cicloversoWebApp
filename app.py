from flask import Flask, render_template, redirect, url_for, session
from flask_session import Session
from flask_cors import CORS
from flask_mail import Mail
from utils.generaSlotAuto import genera_slot_mensile_escludendo_weekend
import config
import secrets
import sqlite3
import os

from database import init_db
from initadmin import inserisci_admin

# 🔧 Inizializza app Flask
app = Flask(__name__)
CORS(app)

# 🔐 Secret key
app.secret_key = secrets.token_hex(16)

# 🔄 Sessione su filesystem
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# 📩 Configurazione mail direttamente nel file
app.config['MAIL_SERVER'] = config.MAIL_SERVER
app.config['MAIL_PORT'] = config.MAIL_PORT
app.config['MAIL_USE_TLS'] = config.MAIL_USE_TLS
app.config['MAIL_USERNAME'] = config.MAIL_USERNAME
app.config['MAIL_PASSWORD'] = config.MAIL_PASSWORD


mail = Mail(app)

# 📂 Cartella upload
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 📦 Blueprints
from routes.admin import admin_bp
from routes.auth import auth_bp
from routes.api import api_bp
from routes.user import user_bp

app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(auth_bp)
app.register_blueprint(api_bp, url_prefix='/api')
app.register_blueprint(user_bp, url_prefix='/utente')

#ROUTES pubbliche
@app.route('/')
def index():
    return render_template('basic/index.html')

@app.route('/assistenza')
def assitenza():
    return render_template("categoria/assistenza.html")

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

@app.route('/userprenotazione')
def userprenotazione():
    return render_template("categoria/calendario_prenotazioni.html")

@app.route('/profilo')
def profiloUtente():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return redirect(url_for('utente.profilo'))

# Filtro per formattare date
@app.template_filter('datetimeformat')
def datetimeformat(value, format='%d/%m/%Y'):
    try:
        from datetime import datetime
        return datetime.strptime(value, '%Y-%m-%d').strftime(format)
    except:
        return value

@app.template_filter('to_datetime')
def to_datetime_filter(value, format='%Y-%m-%d %H:%M'):
    from datetime import datetime
    return datetime.strptime(value, format)

@app.context_processor
def inject_now():
    from datetime import datetime
    return {'current_time': datetime.now()}

# Avvio app con setup iniziale DB
if __name__ == '__main__':
    init_db()
    inserisci_admin(
        nome='Admin',
        cognome='Admin',
        email='admin@example.com',
        cellulare='1234567890',
        password='Admin100.',
        ruolo='admin'
    )
    inserisci_admin(
        nome='Test',
        cognome='User',
        email='test@example.com',
        cellulare='9876543210',
        password='Test100.',
        ruolo='utente'
    )
    genera_slot_mensile_escludendo_weekend()
    app.run(debug=True)
