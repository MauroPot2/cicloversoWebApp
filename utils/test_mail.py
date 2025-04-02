from flask import Flask
from flask_mail import Mail
from utils.email_utils import invia_mail_benvenuto
import config

app = Flask(__name__)

# 📬 Configurazione della mail (puoi usare direttamente config.py)
app.config['MAIL_SERVER'] = config.MAIL_SERVER
app.config['MAIL_PORT'] = config.MAIL_PORT
app.config['MAIL_USE_TLS'] = config.MAIL_USE_TLS
app.config['MAIL_USERNAME'] = config.MAIL_USERNAME
app.config['MAIL_PASSWORD'] = config.MAIL_PASSWORD

# 🔁 Inizializza Flask-Mail
mail = Mail(app)

# 💌 Test invio mail di benvenuto
with app.app_context():
    try:
        invia_mail_benvenuto("santorotundo88@gmail.com", "Santo", mail)
        print("✅ Mail inviata con successo!")
    except Exception as e:
        print(f"❌ Errore nell'invio della mail: {e}")
