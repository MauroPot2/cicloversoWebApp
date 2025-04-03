from flask import current_app, render_template
from flask_mail import Message
from extension import mail
from config import MAIL_USERNAME

def invia_mail_benvenuto(email, nome):
    msg = Message("Benvenuto su CicloVerso 🚴", sender="noreply@cicloverso.it", recipients=[email])
    msg.body = f"Ciao {nome}, grazie per esserti registrato su CicloVerso!"
    msg.html = render_template("email/benvenuto.html", nome=nome)
    mail.send(msg)

def invia_mail_modifica_prenotazione(email, nome, nuova_data):
    mail = current_app.extensions.get('mail')
    if not mail:
        raise RuntimeError("Mail non disponibile.")
    
    msg = Message(
        subject="📅 Modifica prenotazione",
        sender=MAIL_USERNAME,
        recipients=[email]
    )
    msg.body = f"Ciao {nome},\n\nLa tua prenotazione è stata modificata.\nNuova data: {nuova_data}\n\nGrazie!"
    mail.send(msg)

def invia_mail_annullamento(email, nome, data):
    mail = current_app.extensions.get('mail')
    if not mail:
        raise RuntimeError("Mail non disponibile.")
    
    msg = Message(
        subject="❌ Prenotazione annullata",
        sender=MAIL_USERNAME,
        recipients=[email]
    )
    msg.body = f"Ciao {nome},\n\nLa tua prenotazione del {data} è stata annullata.\n\nCi dispiace, a presto!"
    mail.send(msg)
