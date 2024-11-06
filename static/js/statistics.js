document.addEventListener('DOMContentLoaded', function() {
    fetchAndDisplayStats();
});

async function fetchAndDisplayStats() {
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();
        
        const ctx = document.getElementById('salesChart').getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.map(item => item.name),
                datasets: [{
                    label: 'Sales Count',
                    data: data.map(item => item.sales),
                    backgroundColor: 'rgba(54, 162, 235, 0.5)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error fetching statistics:', error);
    }
}
