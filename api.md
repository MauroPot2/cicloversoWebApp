#Definizione API per creare un nuovo slot di prenotazione

POST /admin/crea_slot

#Body JSON:
{
  "data": "2025-04-01",
  "ora_inizio": "10:00",
  "ora_fine": "10:30",
  "servizio": 3
}

#Risposta JSON:
{ "message": "Slot creato con successo" }

#Errore JSON:
{ "error": "Campo mancante o formato errato" }
