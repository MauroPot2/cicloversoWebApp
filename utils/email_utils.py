from flask import current_app
from flask_mail import Message
from config import MAIL_USERNAME

def invia_mail_benvenuto(email_destinatario, nome, mail=None):
    if not mail:
        mail = current_app.extensions.get('mail')

    if not mail:
        raise RuntimeError("Il servizio mail non è disponibile.")

    msg = Message(
        subject="🎉 Benvenuto su Cicloverso!",
        sender=MAIL_USERNAME,
        recipients=[email_destinatario]
    )

    msg.body = f"""
Ciao {nome},

Benvenuto su Cicloverso! 🚴‍♂️

Siamo felici di averti con noi. Da oggi potrai gestire le tue prenotazioni con semplicità e velocità.

A presto,
Il team Cicloverso
"""

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
