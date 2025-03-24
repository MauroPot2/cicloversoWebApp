from datetime import datetime
import sqlite3

class Slot:
    def __init__(self, data, orario, servizio_id=None, disponibile=True):
        self.data = data
        self.orario = orario
        self.servizio_id = servizio_id
        self.disponibile = disponibile

    def save(self):
        """Salva lo slot nel database."""
        conn = sqlite3.connect('usersdb.db')
        cursore = conn.cursor()
        cursore.execute("INSERT OR IGNORE INTO slot_disponibili (data, orario, servizio_id, disponibile) VALUES (?, ?, ?, ?)",
                       (self.data.isoformat(), self.orario.isoformat(), self.servizio_id, int(self.disponibile)))
        conn.commit()
        conn.close()

    @staticmethod
    def get_slots_by_date(data):
        """Recupera gli slot disponibili per una data specifica."""
        conn = sqlite3.connect('usersdb.db')
        cursore = conn.cursor()
        cursore.execute("SELECT orario, servizio_id, disponibile FROM slot_disponibili WHERE data = ?", (data.isoformat(),))
        slots_data = cursore.fetchall()
        conn.close()

        slots = []
        for orario, servizio_id, disponibile in slots_data:
            slots.append(Slot(data, datetime.strptime(orario, '%H:%M:%S').time(), servizio_id, bool(disponibile)))
        return slots

    @staticmethod
    def get_available_slots_by_date(data):
        """Recupera gli slot disponibili e non prenotati per una data specifica."""
        conn = sqlite3.connect('usersdb.db')
        cursore = conn.cursor()
        cursore.execute("SELECT orario, servizio_id FROM slot_disponibili WHERE data = ? AND disponibile = 1", (data.isoformat(),))
        slots_data = cursore.fetchall()
        conn.close()

        slots = []
        for orario, servizio_id in slots_data:
            slots.append(Slot(data, datetime.strptime(orario, '%H:%M:%S').time(), servizio_id))
        return slots

    def __repr__(self):
        return f"Slot(data={self.data}, orario={self.orario}, servizio_id={self.servizio_id}, disponibile={self.disponibile})"