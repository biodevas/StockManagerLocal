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
    
    // Add event listeners for export buttons
    document.getElementById('exportSales').addEventListener('click', () => exportData('sales'));
    document.getElementById('exportTransactions').addEventListener('click', () => exportData('transactions'));
    
    fetchAndDisplayStats();
});

async function fetchAndDisplayStats() {
    try {
        const startDate = document.getElementById('startDate').value;
        const endDate = document.getElementById('endDate').value;
        
        const response = await fetch(`/api/stats?start_date=${startDate}&end_date=${endDate}`);
        const data = await response.json();
        
        // Update total sales
        document.getElementById('totalSales').textContent = data.total_sales;
        
        // Sort sales data by quantity in descending order
        const sortedSalesData = [...data.sales_data].sort((a, b) => b.sales - a.sales);
        
        // Update product ranking
        const rankingContainer = document.getElementById('productRanking');
        rankingContainer.innerHTML = '';
        
        sortedSalesData.forEach((product, index) => {
            const rankingItem = document.createElement('div');
            rankingItem.className = 'list-group-item d-flex justify-content-between align-items-center';
            
            const rankBadge = document.createElement('span');
            rankBadge.className = 'badge bg-primary rounded-pill me-2';
            rankBadge.textContent = `#${index + 1}`;
            
            const productInfo = document.createElement('div');
            productInfo.className = 'd-flex flex-column flex-grow-1';
            productInfo.innerHTML = `
                <div class="fw-bold">${product.name}</div>
                <small class="text-muted">Ventas: ${product.sales}</small>
                <small class="text-muted">Usuario: ${product.user}</small>
            `;
            
            rankingItem.appendChild(rankBadge);
            rankingItem.appendChild(productInfo);
            rankingContainer.appendChild(rankingItem);
        });
        
        // Create the chart
        const ctx = document.getElementById('salesChart').getContext('2d');
        
        // Destroy existing chart if it exists
        if (window.salesChart instanceof Chart) {
            window.salesChart.destroy();
        }
        
        window.salesChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: sortedSalesData.map(item => `${item.name} (${item.user})`),
                datasets: [{
                    label: 'Ventas',
                    data: sortedSalesData.map(item => item.sales),
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
                    },
                    x: {
                        ticks: {
                            maxRotation: 45,
                            minRotation: 45
                        }
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Ventas por Producto y Usuario'
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

async function exportData(type) {
    try {
        const startDate = document.getElementById('startDate').value;
        const endDate = document.getElementById('endDate').value;
        
        // Create a hidden anchor element for download
        const link = document.createElement('a');
        link.style.display = 'none';
        document.body.appendChild(link);
        
        // Get the export URL
        const url = `/api/export/${type}?start_date=${startDate}&end_date=${endDate}`;
        
        // Trigger the download
        window.location.href = url;
        
        // Clean up
        document.body.removeChild(link);
    } catch (error) {
        console.error(`Error exporting ${type}:`, error);
    }
}
