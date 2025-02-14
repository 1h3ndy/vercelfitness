
document.addEventListener('DOMContentLoaded', fetchWeightLog);


document.getElementById('weightForm').addEventListener('submit', addWeight);


async function fetchWeightLog() {
    const response = await fetch('/api/get-weight-log');
    console.log(response);
    if (response.ok) {
        const data = await response.json();
        const dates = data.weight_log.map(entry => entry.date); // entry is just json entries, map converts to array/list
        const weights = data.weight_log.map(entry => entry.weight);

        renderChart(dates, weights);
        console.log(dates + weights);
    } else {
        console.error('eror');
    }
}

async function addWeight(event) {
    event.preventDefault();
    const weight = document.getElementById('weight').value;

    const response = await fetch('/api/add-weight', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ weight })
    });

    if (response.ok) {
        alert('Weight logged');
        fetchWeightLog();
    } else {
        console.error('Failed');
    }
}

function renderChart(dates, weights) {
    const ctx = document.getElementById('weightChart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [{
                label: 'Weight (kg)',
                data: weights,
                borderColor: 'red',
                borderWidth: 2,
                fill: false
            }]
        },
        options: {
            responsive: true,
            scales: {
                x: { title: { display: true, text: 'Date' } },
                y: { title: { display: true, text: 'Weight (kg)' } }
            }
        }
    });
}
