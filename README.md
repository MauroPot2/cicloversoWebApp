
# 🚴 CicloVerso – Web App per Servizi di Ciclomeccanica

![Badge](https://img.shields.io/badge/Python-3.11-blue.svg) ![Badge](https://img.shields.io/badge/Flask-3.0.2-green.svg) ![Badge](https://img.shields.io/badge/Bootstrap-5.3.3-purple.svg) ![Badge](https://img.shields.io/badge/SQLite3-Database-orange.svg)

CicloVerso è un'applicazione web sviluppata in Python con Flask per la gestione completa e intuitiva delle prenotazioni di servizi di ciclomeccanica, rivolto sia ai clienti che agli amministratori del negozio.

## 📌 Caratteristiche principali

- ✅ **Gestione utenti**
  - Registrazione, login e recupero password
  - Profilo personale e gestione prenotazioni utente

- ✅ **Sistema di prenotazione avanzato**
  - Calendario interattivo basato su FullCalendar.js
  - Prenotazione facile e immediata degli slot disponibili

- ✅ **Dashboard Amministrativa**
  - Gestione dinamica degli slot prenotabili
  - Funzionalità CRUD per utenti e servizi offerti
  - Gestione orari apertura e durata slot personalizzabile

- ✅ **Responsive & Mobile First**
  - Progettato per un’esperienza utente ottimale su dispositivi desktop e mobile

## 🛠️ Tecnologie utilizzate

- **Backend**
  - Python 3.11
  - Flask 3.0.2
  - SQLite3
  
- **Frontend**
  - HTML5, CSS3, JavaScript
  - Bootstrap 5.3.3
  - FullCalendar.js 6.1.8
  - Icone Bootstrap

## ⚙️ Installazione locale e avvio rapido

### Prerequisiti:

- Python 3.11+
- SQLite3 installato sul sistema

### Step per la configurazione:

°°°Attenzione se ignori questo passaggio l'app andrà in crash°°°
L'applicazione offre un servizio di mailing che consente agli utente di ricevere una mail di benvenuto dopo essersi registrati in piattaforma.
Aggiungi nel root della webApp il file config.py e alimentalo con i seguenti dati:

```python
# config.py
MAIL_SERVER = 'tuo nome server'
MAIL_PORT = 'tuo numero porta'
MAIL_USE_TLS = True
MAIL_USERNAME = 'tuamail@mail.com'
MAIL_PASSWORD = 'tua password' # se usi gmail hai bisogno di una password
                                per le app per evitare l'autenticazione
                                a due fattori che trovi qua -> https://myaccount.google.com/apppasswords
```

1. Clona il repository da GitHub:

```bash
git clone https://github.com/tuo-username/cicloversoWebApp.git
cd cicloversoWebApp
```

2. Crea un ambiente virtuale e attivalo:

```bash
python -m venv venv
source venv/bin/activate   # per Windows usa: venv\Scripts\activate
```

3. Installa le dipendenze:

```bash
pip install -r requirements.txt
```


4. Avvia l'applicazione Flask:

```bash
python app.py
```

5. Visita l'applicazione all'indirizzo `http://localhost:5000`.

All'avvio l'applicazione alimenterá il database con due utenti prova:

L'utente admin dovrá accedere al sito con le credenziali:
Mail     ->  admin@example.com
Password ->  Admin100.

Il normale utente dovrá accedere al sito con le credenziali:
Mail     -> test@example.com
Password -> Test100.

All'avvio dell'applicazione si autocompilerá il calendario con gli slot disponibili,
si potrá pertanto testare da subito la prenotazione degli slot.

## 🚀 Roadmap per sviluppi futuri

- [ ] Integrazione pagamenti online
- [ ] Notifiche push e SMS
- [ ] Reportistica avanzata delle attività amministrative
- [ ] Supporto multi-negozio/multi-filiale

## 🤝 Contribuire

Le contribuzioni sono sempre benvenute!  

Se desideri contribuire, segui questi step:

1. Fork del repository
2. Crea un nuovo branch (`git checkout -b nuova-funzionalita`)
3. Esegui il commit delle modifiche (`git commit -m 'Aggiunta funzionalità X'`)
4. Push al branch (`git push origin nuova-funzionalita`)
5. Apri una Pull Request

## 📞 Contatti e Supporto

Per qualsiasi dubbio, suggerimento o collaborazione:

- **Email**: mauroleonardo.potestio@gmail.com

## 📝 Licenza

Questo progetto è rilasciato sotto licenza MIT.  
Per maggiori informazioni leggi il file [LICENSE](LICENSE).
