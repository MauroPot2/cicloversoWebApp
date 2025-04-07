from datetime import datetime, timedelta
import sqlite3
from slot import Slot

def genera_slot_per_data(data):
    conn = sqlite3.connect('usersdb.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM orari_apertura LIMIT 1")
    orari = cursor.fetchone()
    durata_slot = int(orari['durata_slot'])

    # 🧼 Rimuovi gli slot già esistenti per quel giorno
    cursor.execute("DELETE FROM slot WHERE data = ?", (data.isoformat(),))
    conn.commit()

    def genera_intervalli(inizio_str, fine_str):
        inizio = datetime.strptime(inizio_str, '%H:%M')
        fine = datetime.strptime(fine_str, '%H:%M')
        while inizio + timedelta(minutes=durata_slot) <= fine:
            yield inizio.time(), (inizio + timedelta(minutes=durata_slot)).time()
            inizio += timedelta(minutes=durata_slot)

    for ora_inizio, ora_fine in genera_intervalli(orari['apertura_mattina'], orari['chiusura_mattina']):
        slot = Slot(data, ora_inizio, ora_fine)
        slot.save()

    for ora_inizio, ora_fine in genera_intervalli(orari['apertura_pomeriggio'], orari['chiusura_pomeriggio']):
        slot = Slot(data, ora_inizio, ora_fine)
        slot.save()

    conn.close()


def genera_slot_mensile_escludendo_weekend():
    oggi = datetime.now().date()
    primo_giorno = oggi + timedelta(days=1)
    ultimo_giorno = (primo_giorno.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)

    giorno_corrente = primo_giorno

    while giorno_corrente <= ultimo_giorno:
        if giorno_corrente.weekday() < 5:  # 0 = lunedì, ..., 4 = venerdì
            try:
                genera_slot_per_data(giorno_corrente)
            except Exception as e:
                print(f"Errore generando slot per il {giorno_corrente}: {e}")
        giorno_corrente += timedelta(days=1)
