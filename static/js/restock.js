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
            nameInput.value = selectedOption.text;
            nameInput.readOnly = true;
            priceInput.value = selectedOption.dataset.price;
            priceInput.readOnly = true;
            imageUploadContainer.style.display = 'none';
            imageInput.required = false;
            imageInput.value = ''; // Clear any selected file
        }
    });
});
