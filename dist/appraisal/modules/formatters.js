// ==================== FORMATTERS MODULE ====================
export function formatPhoneNumber(input) {
    let value = input.value.replace(/\s/g, '');
    if (value.startsWith('3') && !value.startsWith('+')) value = '+39' + value;
    if (value.startsWith('+39') && value.length > 5) {
        const digits = value.substring(3);
        if (digits.length > 3) value = `+39 ${digits.substring(0, 3)} ${digits.substring(3)}`;
    }
    input.value = value;
}

export function formatPostalCode(input) {
    let value = input.value.replace(/[^0-9]/g, '').substring(0, 5);
    input.value = value;
}
