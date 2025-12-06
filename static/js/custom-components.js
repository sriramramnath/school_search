// Custom Dropdown and Radio Button Components

document.addEventListener('DOMContentLoaded', function() {
    // Initialize custom dropdowns
    document.querySelectorAll('select.form-select, select.form-field-select').forEach(select => {
        createCustomDropdown(select);
    });
    
    // Initialize custom radio buttons
    document.querySelectorAll('input[type="radio"]').forEach(radio => {
        createCustomRadio(radio);
    });
});

function createCustomDropdown(select) {
    // Create wrapper
    const wrapper = document.createElement('div');
    wrapper.className = 'custom-dropdown';
    
    // Create trigger
    const trigger = document.createElement('div');
    trigger.className = 'custom-dropdown-trigger';
    const selectedOption = select.options[select.selectedIndex];
    trigger.innerHTML = `
        <span class="custom-dropdown-text">${selectedOption ? selectedOption.text : 'Select...'}</span>
        <span class="material-icons">expand_more</span>
    `;
    
    // Create menu
    const menu = document.createElement('div');
    menu.className = 'custom-dropdown-menu';
    
    // Create options
    Array.from(select.options).forEach((option, index) => {
        const optionEl = document.createElement('div');
        optionEl.className = 'custom-dropdown-option';
        if (option.selected) optionEl.classList.add('selected');
        optionEl.textContent = option.text;
        optionEl.dataset.value = option.value;
        
        optionEl.addEventListener('click', () => {
            select.value = option.value;
            select.dispatchEvent(new Event('change', { bubbles: true }));
            trigger.querySelector('.custom-dropdown-text').textContent = option.text;
            menu.querySelectorAll('.custom-dropdown-option').forEach(opt => opt.classList.remove('selected'));
            optionEl.classList.add('selected');
            trigger.classList.remove('active');
            menu.classList.remove('active');
        });
        
        menu.appendChild(optionEl);
    });
    
    // Toggle menu
    trigger.addEventListener('click', (e) => {
        e.stopPropagation();
        const isActive = trigger.classList.contains('active');
        
        // Close all other dropdowns
        document.querySelectorAll('.custom-dropdown-trigger').forEach(t => {
            t.classList.remove('active');
            t.nextElementSibling?.classList.remove('active');
        });
        
        if (!isActive) {
            trigger.classList.add('active');
            menu.classList.add('active');
        }
    });
    
    // Close on outside click
    document.addEventListener('click', (e) => {
        if (!wrapper.contains(e.target)) {
            trigger.classList.remove('active');
            menu.classList.remove('active');
        }
    });
    
    // Replace select with custom dropdown
    select.style.display = 'none';
    wrapper.appendChild(trigger);
    wrapper.appendChild(menu);
    select.parentNode.insertBefore(wrapper, select);
    wrapper.appendChild(select);
}

function createCustomRadio(radio) {
    // Create wrapper
    const wrapper = document.createElement('label');
    wrapper.className = 'custom-radio';
    
    // Create indicator
    const indicator = document.createElement('span');
    indicator.className = 'custom-radio-indicator';
    
    // Create label
    const label = document.createElement('span');
    label.className = 'custom-radio-label';
    
    // Get label text from parent or sibling
    const parentLabel = radio.closest('label');
    if (parentLabel) {
        label.textContent = parentLabel.textContent.replace(radio.value, '').trim();
    } else {
        const labelElement = document.querySelector(`label[for="${radio.id}"]`);
        if (labelElement) {
            label.textContent = labelElement.textContent;
        } else {
            label.textContent = radio.value;
        }
    }
    
    // Clone radio button
    const radioClone = radio.cloneNode(true);
    radioClone.style.display = 'none';
    
    // Build structure
    wrapper.appendChild(radioClone);
    wrapper.appendChild(indicator);
    wrapper.appendChild(label);
    
    // Replace original
    if (radio.parentNode) {
        radio.parentNode.replaceChild(wrapper, radio);
    }
    
    // Handle clicks
    wrapper.addEventListener('click', () => {
        radioClone.checked = true;
        radioClone.dispatchEvent(new Event('change', { bubbles: true }));
    });
}

