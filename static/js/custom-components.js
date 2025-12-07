// Custom Dropdown and Radio Button Components

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Choices.js for form-select only (keep form-field-select native)
    document.querySelectorAll('select.form-select').forEach(select => {
        // Skip if already initialized
        if (select.hasAttribute('data-choice')) {
            return;
        }
        
        const choices = new Choices(select, {
            searchEnabled: false,
            itemSelectText: '',
            shouldSort: false,
            classNames: {
                containerOuter: 'choices choices-select',
                containerInner: 'choices__inner',
                input: 'choices__input',
                inputCloned: 'choices__input--cloned',
                list: 'choices__list',
                listItems: 'choices__list--multiple',
                listSingle: 'choices__list--single',
                listDropdown: 'choices__list--dropdown',
                item: 'choices__item',
                itemSelectable: 'choices__item--selectable',
                itemDisabled: 'choices__item--disabled',
                itemChoice: 'choices__item--choice',
                placeholder: 'choices__placeholder',
                group: 'choices__group',
                groupHeading: 'choices__heading',
                button: 'choices__button',
                activeState: 'is-active',
                focusState: 'is-focused',
                openState: 'is-open',
                disabledState: 'is-disabled',
                highlightedState: 'is-highlighted',
                selectedState: 'is-selected',
                flippedState: 'is-flipped',
                loadingState: 'is-loading',
                noResults: 'has-no-results',
                noChoices: 'has-no-choices'
            }
        });
        
        // Mark as initialized
        select.setAttribute('data-choice', 'true');
    });
    
    // Initialize custom radio buttons
    document.querySelectorAll('input[type="radio"]').forEach(radio => {
        createCustomRadio(radio);
    });
});

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

