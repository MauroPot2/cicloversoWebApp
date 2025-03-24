from flask import Flask, render_template
from flask_session import Session
from flask_mail import Mail
from flask_cors import CORS
import secrets
import config
import sqlite3

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

# Registrazione dei blueprint
from blueprints.admin import admin_bp
from blueprints.auth import auth_bp
from blueprints.servizi import servizi_bp
from blueprints.prenotazioni import prenotazioni_bp
from blueprints.api import api_bp

app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(auth_bp)
app.register_blueprint(servizi_bp, url_prefix='/admin')
app.register_blueprint(prenotazioni_bp)
app.register_blueprint(api_bp, url_prefix='/api')

# Route principale per la home page
@app.route('/')
def index():
    return render_template('index.html')

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

if __name__ == '__main__':
    app.run(debug=True)