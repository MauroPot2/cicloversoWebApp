from datetime import datetime
import sqlite3

class Slot:
    def __init__(self, data, ora_inizio, ora_fine, servizio_id=None, disponibile=True):
        self.data = data
        self.ora_inizio = ora_inizio
        self.ora_fine = ora_fine
        self.servizio_id = servizio_id
        self.disponibile = disponibile

    def save(self):
        """Salva lo slot nel database."""
        conn = sqlite3.connect('usersdb.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR IGNORE INTO slot (data, ora_inizio, ora_fine, servizio_id, disponibile)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            self.data.isoformat(),
            self.ora_inizio.isoformat(),
            self.ora_fine.isoformat(),
            self.servizio_id,
            int(self.disponibile)
        ))
        conn.commit()
        conn.close()

    @staticmethod
    def get_slots_by_date(data):
        """Recupera tutti gli slot per una data specifica."""
        conn = sqlite3.connect('usersdb.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('''
            SELECT ora_inizio, ora_fine, servizio_id, disponibile
            FROM slot
            WHERE data = ?
        ''', (data.isoformat(),))
        rows = cursor.fetchall()
        conn.close()

        slots = []
        for row in rows:
            slots.append(Slot(
                data=data,
                ora_inizio=datetime.strptime(row['ora_inizio'], '%H:%M:%S').time(),
                ora_fine=datetime.strptime(row['ora_fine'], '%H:%M:%S').time(),
                servizio_id=row['servizio_id'],
                disponibile=bool(row['disponibile'])
            ))
        return slots

    @staticmethod
    def get_available_slots_by_date(data):
        """Recupera solo gli slot disponibili per una data specifica."""
        conn = sqlite3.connect('usersdb.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('''
            SELECT ora_inizio, ora_fine, servizio_id
            FROM slot
            WHERE data = ? AND disponibile = 1
        ''', (data.isoformat(),))
        rows = cursor.fetchall()
        conn.close()

        slots = []
        for row in rows:
            slots.append(Slot(
                data=data,
                ora_inizio=datetime.strptime(row['ora_inizio'], '%H:%M:%S').time(),
                ora_fine=datetime.strptime(row['ora_fine'], '%H:%M:%S').time(),
                servizio_id=row['servizio_id'],
                disponibile=True
            ))
        return slots

    def __repr__(self):
        return f"Slot(data={self.data}, ora_inizio={self.ora_inizio}, ora_fine={self.ora_fine}, servizio_id={self.servizio_id}, disponibile={self.disponibile})"
