let slots = [];

const adminButton = document.getElementById("adminButton");
const adminModal = new bootstrap.Modal(document.getElementById('adminModal'), {});
const saveSlotButton = document.getElementById("saveSlotButton");
const slotStartTimeInput = document.getElementById("slotStartTime");
const slotEndTimeInput = document.getElementById("slotEndTime");
const slotServiceInput = document.getElementById("slotService");

adminButton.addEventListener("click", () => {
    adminModal.show();
});

saveSlotButton.addEventListener("click", () => {
    const start = slotStartTimeInput.value;
    const end = slotEndTimeInput.value;
    const service = slotServiceInput.value;
    if (start && end && service) {
        slots.push({ start, end, service });
        //Assicurati che generateCalendar sia definito prima di chiamarlo.
        if (typeof generateCalendar === 'function') {
            generateCalendar(currentDate, currentView);
        }
        adminModal.hide();
    } else {
        alert("Compila tutti i campi.");
    }
});