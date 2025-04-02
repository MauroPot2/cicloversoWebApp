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
