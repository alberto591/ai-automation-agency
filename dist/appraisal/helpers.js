// ==================== LOADING PROGRESS SYSTEM ====================
function showLoadingProgress(message, progress) {
    let overlay = document.getElementById('loading-overlay');
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.id = 'loading-overlay';
        overlay.innerHTML = `
            <div class="loading-content">
                <div class="loading-spinner"></div>
                <div class="loading-message" id="loading-message"></div>
                <div class="progress-bar-container">
                    <div class="progress-bar" id="progress-bar"></div>
                </div>
                <div class="progress-text" id="progress-text">0%</div>
            </div>
        `;
        document.body.appendChild(overlay);
    }
    overlay.classList.add('active');
    document.getElementById('loading-message').textContent = message;
    document.getElementById('progress-bar').style.width = `${progress}%`;
    document.getElementById('progress-text').textContent = `${Math.round(progress)}%`;
}

function hideLoadingProgress() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) overlay.classList.remove('active');
}

// ==================== FORM VALIDATORS ====================
const validators = {
    postalCode: (value) => /^[0-9]{5}$/.test(value),
    phone: (value) => /^(\+39|0039|\+34|0034)?[0-9]{9,10}$/.test(value.replace(/\s/g, '')),
    sqm: (value) => { const n = parseInt(value.replace(/,/g, '')); return n >= 20 && n <= 500; },
    address: (value) => value.length >= 5 && value.length <= 200
};

function validateField(field, validator) {
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

// ==================== AUTO-FORMATTING ====================
function formatPhoneNumber(input) {
    let value = input.value.replace(/\s/g, '');
    if (value.startsWith('3') && !value.startsWith('+')) value = '+39' + value;
    if (value.startsWith('+39') && value.length > 5) {
        const digits = value.substring(3);
        if (digits.length > 3) value = `+39 ${digits.substring(0, 3)} ${digits.substring(3)}`;
    }
    input.value = value;
}

function formatPostalCode(input) {
    let value = input.value.replace(/[^0-9]/g, '').substring(0, 5);
    input.value = value;
}

// ==================== CLIENT-SIDE CACHE ====================
const appraisalCache = {
    storage: new Map(),
    ttl: 15 * 60 * 1000,
    generateKey(p) { return `${p.city}_${p.zone}_${p.surface_sqm}_${p.condition}`; },
    get(params) {
        const cached = this.storage.get(this.generateKey(params));
        if (!cached || Date.now() - cached.timestamp > this.ttl) return null;
        return cached.data;
    },
    set(params, data) {
        this.storage.set(this.generateKey(params), { data, timestamp: Date.now() });
    }
};

// ==================== DISPLAY RESULTS HELPER ====================
function displayAppraisalResults(appraisal, submitBtn) {
    // Show Instant Result UI
    document.querySelector('.appraisal-form-box').style.display = 'none';
    const resultBox = document.getElementById('appraisal-result');
    resultBox.style.display = 'block';

    // Extract real data from API response
    const metrics = appraisal.investment_metrics || {};
    const hasData = appraisal.estimated_value > 0;

    // Toggle result UI based on data availability
    const noDataAlert = document.getElementById('no-data-alert');
    const valueRangeDisplay = document.getElementById('value-range');
    if (noDataAlert && valueRangeDisplay) {
        noDataAlert.style.display = hasData ? 'none' : 'flex';
        valueRangeDisplay.style.display = hasData ? 'block' : 'none';
    }

    // Update Confidence Text
    const confidenceText = document.getElementById('confidence-text');
    if (confidenceText) {
        if (hasData && appraisal.confidence_level) {
            const stars = '⭐'.repeat(appraisal.reliability_stars || 3);
            confidenceText.textContent = `${stars} (${appraisal.confidence_level}%)`;
        } else {
            confidenceText.textContent = t('appraisal-res-confidence-low');
        }
    }

    // Check if backend is in test mode (instant display)
    const isTestMode = appraisal.reasoning?.includes('TEST MODE');

    if (isTestMode) {
        // Instant display (no animation) for ultra-fast testing
        document.getElementById('res-min').innerHTML = (appraisal.estimated_range_min || 0).toLocaleString();
        document.getElementById('res-max').innerHTML = (appraisal.estimated_range_max || 0).toLocaleString();
        document.getElementById('res-sqm').innerHTML = (appraisal.avg_price_sqm || 0).toLocaleString();

        if (metrics && Object.keys(metrics).length > 0 && hasData) {
            document.getElementById('res-rent').innerHTML = (metrics.monthly_rent || 0).toLocaleString();
            document.getElementById('res-yield').innerHTML = (metrics.cap_rate || 0).toFixed(1);
            document.getElementById('res-cap-rate').innerHTML = (metrics.cap_rate || 0).toFixed(1);
            document.getElementById('res-roi').innerHTML = (metrics.roi || 0).toFixed(1);
            document.getElementById('res-coc').innerHTML = (metrics.cash_on_cash_return || 0).toFixed(1);
        }
    } else {
        // Animate with real data (faster for testing)
        animateValue("res-min", 0, appraisal.estimated_range_min || 0, 500);
        animateValue("res-max", 0, appraisal.estimated_range_max || 0, 500);
        animateValue("res-sqm", 0, appraisal.avg_price_sqm || 0, 500);

        // Use real investment metrics if available
        if (metrics && Object.keys(metrics).length > 0 && hasData) {
            animateValue("res-rent", 0, metrics.monthly_rent || 0, 500);
            animateValue("res-yield", 0, metrics.cap_rate || 0, 500, true);
            animateValue("res-cap-rate", 0, metrics.cap_rate || 0, 500, true);
            animateValue("res-roi", 0, metrics.roi || 0, 500, true);
            animateValue("res-coc", 0, metrics.cash_on_cash_return || 0, 500, true);
        }
    }

    // Reset button state
    submitBtn.innerHTML = `<span data-translate="appraisal-cta">${t('appraisal-cta')}</span> <i class="ph ph-arrow-right"></i>`;
    submitBtn.disabled = false;
}
