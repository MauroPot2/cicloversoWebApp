DROP TABLE IF EXISTS servizi;
DROP TABLE IF EXISTS utenti;
DROP TABLE IF EXISTS prenotazioni;
DROP TABLE IF EXISTS slot;
DROP TABLE IF EXISTS orari_apertura;

CREATE TABLE IF NOT EXISTS slot (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data TEXT,
                ora_inizio TEXT,
                ora_fine TEXT,
                servizio_id INTEGER,
                disponibile INTEGER NOT NULL DEFAULT 1,
                prenotazioni TEXT,
                FOREIGN KEY (servizio_id) REFERENCES servizi(id)
            );

CREATE TABLE IF NOT EXISTS prenotazione (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data_ora DATETIME NOT NULL,
                utente_id INTEGER,
                servizio_id INTEGER,
                FOREIGN KEY (utente_id) REFERENCES utenti(id),
                FOREIGN KEY (servizio_id) REFERENCES servizi(ServiziID)
);

CREATE TABLE IF NOT EXISTS utenti (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome VARCHAR(100),
                cognome VARCHAR(100),
                email VARCHAR(100) UNIQUE,
                cellulare VARCHAR(15) UNIQUE,
                hash_password VARCHAR(256),
                reset_token VARCHAR(256),
                ruolo VARCHAR(20) DEFAULT 'utente'          
);

CREATE TABLE IF NOT EXISTS servizi (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                Servizio VARCHAR(50) NOT NULL,
                Prezzo INTEGER,
                Disponibilitá INTEGER, 
                immagine TEXT NOT NULL 
);

INSERT INTO servizi (Servizio, Prezzo, Disponibilitá, immagine) VALUES (
    'Sostituzione manettino',
    15,
    1,
    'static/img/manettino.png'
);

INSERT INTO servizi (Servizio, Prezzo, Disponibilitá, immagine) VALUES (
    'Sostituzione cambio',
    15,
    1,
    'static/img/cambio.png'
);

CREATE TABLE IF NOT EXISTS orari_apertura (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    apertura_mattina TEXT NOT NULL,
    chiusura_mattina TEXT NOT NULL,
    apertura_pomeriggio TEXT NOT NULL,
    chiusura_pomeriggio TEXT NOT NULL,
    durata_slot INTEGER NOT NULL
);
-- Orario predefinito
INSERT INTO orari_apertura (apertura_mattina, chiusura_mattina, apertura_pomeriggio, chiusura_pomeriggio, durata_slot)
VALUES ('10:00', '12:00', '16:00', '18:00', 60)