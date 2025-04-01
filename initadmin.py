import sqlite3
import bcrypt

def inserisci_admin(nome, cognome, email, cellulare, password, ruolo='admin', database_path='usersdb.db'):
    """Inserisce un utente admin nel database."""

    # Hash della password
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

    try:
        # Connessione al database
        conn = sqlite3.connect(database_path)
        cursore = conn.cursor()

        # Inserimento dell'utente admin
        cursore.execute(
            """
            INSERT INTO utenti (nome, cognome, email, cellulare, hash_password, ruolo)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (nome, cognome, email, cellulare, hashed_password, ruolo)
        )

        # Commit delle modifiche e chiusura della connessione
        conn.commit()
        print("Utente " + nome + " inserito con successo.")

    except sqlite3.Error as e:
        print(f"Errore durante l'inserimento dell'utente admin: {e}")

    finally:
        if 'conn' in locals():
            conn.close()