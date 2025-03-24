const calendar = document.getElementById('calendar');
const currentMonthYear = document.getElementById('currentMonthYear');
const prevMonthButton = document.getElementById('prevMonth');
const nextMonthButton = document.getElementById('nextMonth');
const viewDayButton = document.getElementById('viewDay');
const viewWeekButton = document.getElementById('viewWeek');
const viewMonthButton = document.getElementById('viewMonth');
const currentDaySpan = document.getElementById('currentDay');
const prevDayButton = document.getElementById('prevDay');
const nextDayButton = document.getElementById('nextDay');
const dayControls = document.getElementById('dayControls');

let currentDate = new Date();
let currentView = 'month'; // Inizia con la visualizzazione mensile

async function generateCalendar(date, view) {
    const year = date.getFullYear();
    const month = date.getMonth();
    const firstDay = new Date(year, month, 1).getDay();
    const daysInMonth = new Date(year, month + 1, 0).getDate();
    const today = new Date();

    currentMonthYear.textContent = date.toLocaleDateString('it-IT', { month: 'long', year: 'numeric' });

    let calendarBody = '<tbody>';
    let dayCounter = 1;

    if (view === 'month') {
        for (let i = 0; i < 6; i++) {
            calendarBody += '<tr>';
            for (let j = 0; j < 7; j++) {
                if (i === 0 && j < firstDay) {
                    calendarBody += '<td></td>';
                } else if (dayCounter > daysInMonth) {
                    calendarBody += '<td></td>';
                } else {
                    const isToday = today.getDate() === dayCounter && today.getMonth() === month && today.getFullYear() === year;
                    const dayClass = isToday ? 'today' : '';
                    calendarBody += `<td class="${dayClass}">${dayCounter}</td>`;
                    dayCounter++;
                }
            }
            calendarBody += '</tr>';
        }
    } else if (view === 'week') {
        const startOfWeek = new Date(date);
        startOfWeek.setDate(date.getDate() - date.getDay());

        let calendarBody = '<tr>';
        for (let i = 0; i < 7; i++) {
            const currentDay = new Date(startOfWeek);
            currentDay.setDate(startOfWeek.getDate() + i);

            const isToday = today.getDate() === currentDay.getDate() && today.getMonth() === currentDay.getMonth() && today.getFullYear() === currentDay.getFullYear();
            const dayClass = isToday ? 'today' : '';
            calendarBody += `<td class="<span class="math-inline">\{dayClass\}"\></span>{currentDay.getDate()}`;

            const dataStr = currentDay.toISOString().split('T')[0];
            const url = `/slot_prenotazione?data=${dataStr}`;

            try {
                const response = await fetch(url);
                const slots = await response.json();

                if (response.ok) {
                    slots.forEach(slot => {
                        calendarBody += `<br><span>${slot.orario} - Servizio: <span class="math-inline">\{slot\.servizio\_id\}</span\><button onclick\="prenotaSlot\('</span>{dataStr}', '<span class="math-inline">\{slot\.orario\}', '</span>{slot.servizio_id}')">Prenota</button>`;
                    });
                } else {
                    console.error("Errore nel recupero degli slot:", slots.error);
                    calendarBody += '<br>Errore nel recupero degli slot.';
                }
            } catch (error) {
                console.error("Errore di rete:", error);
                calendarBody += '<br>Errore di rete.';
            }

            calendarBody += '</td>';
        }
        calendarBody += '</tr>';
    } else if (view === 'day') {
        currentDaySpan.textContent = date.toLocaleDateString('it-IT', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' });
        dayControls.style.display = 'flex';
        calendarBody += '<tr>';
        calendarBody += `<td>${date.toLocaleDateString('it-IT', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric'})}</td>`;
        calendarBody += '<td>';

        const dataStr = date.toISOString().split('T')[0]; // Ottieni la data nel formato YYYY-MM-DD
        const url = `/slot_prenotazione?data=${dataStr}`; // Costruisci l'URL corretto

        try {
            const response = await fetch(`/slot_prenotazione?data=${date.toISOString().split('T')[0]}`);
            const slots = await response.json();

            if (response.ok) {
                slots.forEach(slot => {
                    calendarBody += `<tr><td><span>${slot}</span></td><td><button onclick="prenotaSlot('${dataStr}', '${slot}')">Prenota</button></td></tr>`;
                });
            } else {
                console.error("Errore nel recupero degli slot:", slots.error);
                calendarBody += '<tr><td>Errore nel recupero degli slot.</td></tr>';
            }
        } catch (error) {
            console.error("Errore di rete:", error);
            calendarBody += '<tr><td>Errore di rete.</td></tr>';
        }

        calendarBody += '</td>';
        calendarBody += '</tr>';
    }

    calendarBody += '</tbody>';
    calendar.innerHTML = calendarBody;
}

function fetchTimeSlots(date) {
    fetch(`/admin/slot_disponibili?data=${date.toISOString().split('T')[0]}`)
        .then(response => response.json())
        .then(slots => {
            let html = '';
            slots.forEach(slot => {
                const isActive = selectedTime === slot[0];
                const className = isActive ? 'active' : '';
                html += `<li class="list-group-item ${className}" data-time="${slot[0]}">${slot[0]}</li>`;
            });
            document.getElementById('orario').innerHTML = html;

            document.getElementById('data').value = date.toISOString().split('T')[0];

            document.querySelectorAll('#orario li').forEach(slot => {
                slot.addEventListener('click', () => {
                    selectedTime = slot.dataset.time;
                    fetchTimeSlots(date);
                });
            });
        });
    }
async function prenotaSlot(data, orario) {
    try {
        // Effettua una richiesta GET al backend per verificare l'autenticazione
        const authResponse = await fetch('/prenota', {
            method: 'GET',
        });

        // Verifica se la risposta è un reindirizzamento (utente non autenticato)
        if (authResponse.redirected) {
            // Reindirizza l'utente alla pagina di login
            window.location.href = "/log_in";
        } else {
            // L'utente è autenticato, procedi con la prenotazione
            const response = await fetch('/prenota', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ data: data, orario: orario }),
            });

            const result = await response.json();
            if (response.ok) {
                alert(result.messaggio);
            } else {
                alert(result.error);
            }
        }
    } catch (error) {
        alert("Errore di rete durante la prenotazione.");
    }
}

async function inviaPrenotazione() {
    const servizioId = document.getElementById('servizio').value;
    const data = document.getElementById('data').value;
    const orario = document.getElementById('orario').value;

    try {
        const response = await fetch('/prenota', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ servizio_id: servizioId, data: data, orario: orario }),
        });
        const result = await response.json();
            if (response.ok) {
                alert(result.messaggio);
            } else {
                alert(result.error);
            }
        } catch (error) {
        alert("Errore di rete durante la prenotazione.");
    }
}

generateCalendar(currentDate, currentView);

prevDayButton.addEventListener('click', () => {
    currentDate.setDate(currentDate.getDate() - 1);
    generateCalendar(currentDate, currentView);
});

nextDayButton.addEventListener('click', () => {
    currentDate.setDate(currentDate.getDate() + 1);
    generateCalendar(currentDate, currentView);
});

prevMonthButton.addEventListener('click', () => {
    currentDate.setMonth(currentDate.getMonth() - 1);
    generateCalendar(currentDate, currentView);
});

nextMonthButton.addEventListener('click', () => {
    currentDate.setMonth(currentDate.getMonth() + 1);
    generateCalendar(currentDate, currentView);
});

viewDayButton.addEventListener('click', () => {
    currentView = 'day';
    generateCalendar(currentDate, currentView);
    viewDayButton.classList.add('active');
    viewWeekButton.classList.remove('active');
    viewMonthButton.classList.remove('active');
    dayControls.style.display = 'flex'; 
});

viewWeekButton.addEventListener('click', () => {
    currentView = 'week';
    generateCalendar(currentDate, currentView);
    viewDayButton.classList.remove('active');
    viewWeekButton.classList.add('active');
    viewMonthButton.classList.remove('active');
});

viewMonthButton.addEventListener('click', () => {
    currentView = 'month';
    generateCalendar(currentDate, currentView);
    viewDayButton.classList.remove('active');
    viewWeekButton.classList.remove('active');
    viewMonthButton.classList.add('active');
});