// ==================== VALIDATORS MODULE ====================
export const validators = {
    postalCode: (value) => /^[0-9]{5}$/.test(value),
    phone: (value) => /^(\+39|0039|\+34|0034)?[0-9]{9,10}$/.test(value.replace(/\s/g, '')),
    sqm: (value) => { const n = parseInt(value.replace(/,/g, '')); return n >= 20 && n <= 500; },
    address: (value) => value.length >= 5 && value.length <= 200
};

export function validateField(field, validator) {
    const value = field.value;
    const isValid = validator(value);

    if (value) {
        field.classList.toggle('valid', isValid);
        field.classList.toggle('error', !isValid);
    } else {
        field.classList.remove('valid', 'error');
    }

    return isValid;
}
