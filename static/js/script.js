// Main JavaScript file for Claude Code project

document.addEventListener('DOMContentLoaded', function() {
    console.log('Claude Code JavaScript loaded');
    
    // Initialize exercise form numbering
    updateExerciseNumbers();
});

// Function to add a new exercise form
function addExercise() {
    console.log('Add exercise function called');
    
    const formset = document.getElementById('exercise-formset');
    const totalFormsInput = document.getElementById('id_form-TOTAL_FORMS');
    
    if (!formset || !totalFormsInput) {
        console.error('Required elements not found:', { formset, totalFormsInput });
        return;
    }
    
    const currentFormCount = parseInt(totalFormsInput.value);
    console.log('Current form count:', currentFormCount);
    
    // Clone the first exercise form
    const firstForm = formset.querySelector('.exercise-form');
    if (!firstForm) {
        console.error('No exercise form found to clone');
        return;
    }
    
    const newForm = firstForm.cloneNode(true);
    
    // Update form index
    newForm.setAttribute('data-form-index', currentFormCount);
    
    // Clear all input values in the new form
    const inputs = newForm.querySelectorAll('input, select');
    inputs.forEach(input => {
        if (input.type === 'text' || input.type === 'number') {
            input.value = '';
        } else if (input.type === 'select-one') {
            input.selectedIndex = 0;
        }
        
        // Update input names and IDs for the new form
        const name = input.getAttribute('name');
        const id = input.getAttribute('id');
        if (name) {
            const newName = name.replace(/form-\d+/, `form-${currentFormCount}`);
            input.setAttribute('name', newName);
            console.log('Updated name:', name, '->', newName);
        }
        if (id) {
            const newId = id.replace(/form-\d+/, `form-${currentFormCount}`);
            input.setAttribute('id', newId);
            console.log('Updated id:', id, '->', newId);
        }
    });
    
    // Update labels for attributes
    const labels = newForm.querySelectorAll('label');
    labels.forEach(label => {
        const forAttr = label.getAttribute('for');
        if (forAttr) {
            const newFor = forAttr.replace(/form-\d+/, `form-${currentFormCount}`);
            label.setAttribute('for', newFor);
            console.log('Updated for:', forAttr, '->', newFor);
        }
    });
    
    // Clear error messages
    const errorDivs = newForm.querySelectorAll('.error-messages');
    errorDivs.forEach(div => div.remove());
    
    // Ensure remove button exists
    const header = newForm.querySelector('.exercise-header');
    let removeBtn = header.querySelector('.btn-remove-exercise');
    if (!removeBtn) {
        removeBtn = document.createElement('button');
        removeBtn.type = 'button';
        removeBtn.className = 'btn-remove-exercise';
        removeBtn.textContent = 'Remove';
        removeBtn.onclick = function() { removeExercise(this); };
        header.appendChild(removeBtn);
    }
    
    // Append the new form
    formset.appendChild(newForm);
    console.log('New form appended');
    
    // Update total forms count
    totalFormsInput.value = currentFormCount + 1;
    console.log('Updated total forms to:', currentFormCount + 1);
    
    // Update exercise numbers
    updateExerciseNumbers();
}

// Function to remove an exercise form
function removeExercise(button) {
    console.log('Remove exercise function called');
    
    const exerciseForm = button.closest('.exercise-form');
    const formset = document.getElementById('exercise-formset');
    
    // Don't remove if it's the only form
    if (formset.querySelectorAll('.exercise-form').length <= 1) {
        console.log('Cannot remove last exercise form');
        return;
    }
    
    exerciseForm.remove();
    console.log('Exercise form removed');
    
    // Update total forms count
    const totalFormsInput = document.getElementById('id_form-TOTAL_FORMS');
    totalFormsInput.value = parseInt(totalFormsInput.value) - 1;
    
    // Update exercise numbers
    updateExerciseNumbers();
    
    // Re-index all forms
    reindexForms();
}

// Function to update exercise numbers in headers
function updateExerciseNumbers() {
    const exerciseForms = document.querySelectorAll('.exercise-form');
    exerciseForms.forEach((form, index) => {
        const header = form.querySelector('h4');
        if (header) {
            header.textContent = `Exercise ${index + 1}`;
        }
    });
}

// Function to re-index form names and IDs after removal
function reindexForms() {
    const exerciseForms = document.querySelectorAll('.exercise-form');
    exerciseForms.forEach((form, index) => {
        form.setAttribute('data-form-index', index);
        
        const inputs = form.querySelectorAll('input, select');
        inputs.forEach(input => {
            const name = input.getAttribute('name');
            const id = input.getAttribute('id');
            if (name) {
                input.setAttribute('name', name.replace(/form-\d+/, `form-${index}`));
            }
            if (id) {
                input.setAttribute('id', id.replace(/form-\d+/, `form-${index}`));
            }
        });
        
        const labels = form.querySelectorAll('label');
        labels.forEach(label => {
            const forAttr = label.getAttribute('for');
            if (forAttr) {
                label.setAttribute('for', forAttr.replace(/form-\d+/, `form-${index}`));
            }
        });
    });
}