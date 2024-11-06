document.addEventListener('DOMContentLoaded', function() {
    const decreaseButtons = document.querySelectorAll('.decrease-btn');
    
    decreaseButtons.forEach(button => {
        button.addEventListener('click', async function() {
            const beverageId = this.dataset.beverageId;
            try {
                const response = await fetch(`/api/decrease/${beverageId}`, {
                    method: 'POST'
                });
                const data = await response.json();
                
                if (data.success) {
                    const quantityElement = document.querySelector(`#quantity-${beverageId}`);
                    const cardElement = button.closest('.beverage-card');
                    const newQuantity = data.new_quantity;
                    
                    quantityElement.textContent = newQuantity;
                    
                    // Update low stock indicators
                    if (newQuantity < 5) {
                        cardElement.classList.add('low-stock');
                        quantityElement.classList.add('quantity-warning');
                        if (!cardElement.querySelector('.low-stock-badge')) {
                            const badge = document.createElement('div');
                            badge.className = 'low-stock-badge';
                            badge.textContent = '¡Stock Bajo!';
                            cardElement.appendChild(badge);
                        }
                    }
                    
                    // Add animation effect
                    button.classList.add('btn-success');
                    setTimeout(() => button.classList.remove('btn-success'), 200);
                } else {
                    alert('Error: ' + data.error);
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Ocurrió un error al actualizar el inventario');
            }
        });
    });
});
