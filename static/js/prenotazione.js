function formatSlot(slot) {
    return `Orario: ${slot.orario}, Servizio: ${slot.servizio_id}`;
}

function displaySlotDetails(slot) {
    const slotDetails = document.getElementById('slotDetails');
    slotDetails.innerHTML = `
        <h3>Dettagli Slot</h3>
        <p>Orario: ${slot.orario}</p>
        <p>Servizio: ${slot.servizio_id}</p>
    `;
    document.getElementById('prenotaButton').style.display = 'block';
    // Puoi aggiungere qui la logica per gestire la prenotazione dello slot
}

// Assicurati di avere una variabile 'slots' contenente i dati degli slot dal backend
// Esempio: let slots = [{ orario: '10:00', servizio_id: 1 }, { orario: '10:30', servizio_id: 2 }];

// Popola la lista degli slot
let html = '';
slots.forEach(slot => {
    html += `<li class="list-group-item slot-item" data-slot='${JSON.stringify(slot)}'>${formatSlot(slot)}</li>`;
});
document.getElementById('orario').innerHTML = html;

// Aggiungi event listener per mostrare i dettagli dello slot
document.querySelectorAll('.slot-item').forEach(item => {
    item.addEventListener('click', function() {
        const slot = JSON.parse(this.dataset.slot);
        displaySlotDetails(slot);
    });
});