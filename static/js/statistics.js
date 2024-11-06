document.addEventListener('DOMContentLoaded', function() {
    // Set default date range (last 30 days)
    const endDate = new Date();
    const startDate = new Date();
    startDate.setDate(startDate.getDate() - 30);
    
    document.getElementById('startDate').value = startDate.toISOString().split('T')[0];
    document.getElementById('endDate').value = endDate.toISOString().split('T')[0];
    
    // Add event listeners for date inputs
    document.getElementById('startDate').addEventListener('change', fetchAndDisplayStats);
    document.getElementById('endDate').addEventListener('change', fetchAndDisplayStats);
    
    fetchAndDisplayStats();
});

async function fetchAndDisplayStats() {
    try {
        const startDate = document.getElementById('startDate').value;
        const endDate = document.getElementById('endDate').value;
        
        const response = await fetch(`/api/stats?start_date=${startDate}&end_date=${endDate}`);
        const data = await response.json();
        
        // Update summary statistics
        document.getElementById('totalSales').textContent = data.total_sales;
        document.getElementById('topProduct').textContent = data.top_product || '-';
        
        // Create the chart
        const ctx = document.getElementById('salesChart').getContext('2d');
        
        // Destroy existing chart if it exists
        if (window.salesChart instanceof Chart) {
            window.salesChart.destroy();
        }
        
        window.salesChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.sales_data.map(item => item.name),
                datasets: [{
                    label: 'Ventas',
                    data: data.sales_data.map(item => item.sales),
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
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Ventas por Producto'
                    },
                    legend: {
                        display: false
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error fetching statistics:', error);
    }
}
