from flask import Flask, render_template
from flask_session import Session
from flask_mail import Mail
from flask_cors import CORS
from database import init_db
from initadmin import inserisci_admin
import secrets
import config
import sqlite3
import os

app = Flask(__name__)
CORS(app)

# Configurazione della sessione
secret_key = secrets.token_hex(16)
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

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Registrazione dei blueprint
from routes.admin import admin_bp
from routes.auth import auth_bp
from routes.api import api_bp
from routes.user import user_bp

app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(auth_bp, mail=mail)
app.register_blueprint(api_bp, url_prefix='/api')
app.register_blueprint(user_bp, url_prefix='/utente')


# Route principale per la home page
@app.route('/')
def index():
    return render_template('basic/index.html')

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
    return render_template("categoria/profilo.html")

@app.template_filter('datetimeformat')
def datetimeformat(value, format='%d/%m/%Y'):
    try:
        from datetime import datetime
        return datetime.strptime(value, '%Y-%m-%d').strftime(format)
    except:
        return value



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

    app.run(debug=True)