document.addEventListener('DOMContentLoaded', function() {
    const beverageSelect = document.getElementById('beverage-select');
    const nameInput = document.getElementById('name');
    const priceInput = document.getElementById('price');
    const imageUploadContainer = document.getElementById('imageUploadContainer');
    const imageInput = document.getElementById('image');
    
    beverageSelect.addEventListener('change', function() {
        const selectedOption = this.options[this.selectedIndex];
        
        if (selectedOption.value === '') {
            // New beverage selected
            nameInput.value = '';
            nameInput.readOnly = false;
            priceInput.value = '';
            priceInput.readOnly = false;
            imageUploadContainer.style.display = 'block';
            imageInput.required = true;
        } else {
            // Existing beverage selected
            nameInput.value = selectedOption.text.replace(' (Desactivado)', '');
            nameInput.readOnly = true;
            priceInput.value = selectedOption.dataset.price;
            priceInput.readOnly = true;
            imageUploadContainer.style.display = 'none';
            imageInput.required = false;
            imageInput.value = ''; // Clear any selected file
        }
    });

    // Toggle beverage status functionality
    document.querySelectorAll('.toggle-status').forEach(button => {
        button.addEventListener('click', async function() {
            const beverageId = this.dataset.beverageId;
            const isActive = this.dataset.isActive === 'true';
            
            try {
                const response = await fetch(`/api/toggle-beverage/${beverageId}`, {
                    method: 'POST'
                });
                const data = await response.json();
                
                if (data.success) {
                    // Update button appearance and text
                    this.textContent = data.is_active ? 'Desactivar' : 'Activar';
                    this.classList.toggle('btn-warning', data.is_active);
                    this.classList.toggle('btn-success', !data.is_active);
                    this.dataset.isActive = data.is_active;
                    
                    // Update status badge
                    const statusBadge = this.closest('tr').querySelector('.badge');
                    statusBadge.textContent = data.is_active ? 'Activo' : 'Desactivado';
                    statusBadge.classList.toggle('bg-success', data.is_active);
                    statusBadge.classList.toggle('bg-danger', !data.is_active);
                    
                    // Update select option
                    const option = beverageSelect.querySelector(`option[value="${beverageId}"]`);
                    if (option) {
                        const beverageName = option.textContent.replace(' (Desactivado)', '');
                        option.textContent = data.is_active ? beverageName : `${beverageName} (Desactivado)`;
                        option.disabled = !data.is_active;
                    }
                    
                    // Show success message
                    const alert = document.createElement('div');
                    alert.className = 'alert alert-success alert-dismissible fade show';
                    alert.innerHTML = `
                        ${data.message}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    `;
                    document.querySelector('.card-body').insertAdjacentElement('afterbegin', alert);
                }
            } catch (error) {
                console.error('Error:', error);
                const alert = document.createElement('div');
                alert.className = 'alert alert-danger alert-dismissible fade show';
                alert.innerHTML = `
                    Error al actualizar el estado de la bebida
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                `;
                document.querySelector('.card-body').insertAdjacentElement('afterbegin', alert);
            }
        });
    });
});
