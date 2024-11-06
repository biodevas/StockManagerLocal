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
                    quantityElement.textContent = data.new_quantity;
                    
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
