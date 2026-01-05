// ==================== LOADING PROGRESS MODULE ====================
export function showLoadingProgress(message, progress) {
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

export function hideLoadingProgress() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) overlay.classList.remove('active');
}

export function displayAppraisalResults(appraisal, submitBtn) {
    document.querySelector('.appraisal-form-box').style.display = 'none';
    const resultBox = document.getElementById('appraisal-result');
    resultBox.style.display = 'block';

    const metrics = appraisal.investment_metrics || {};
    const hasData = appraisal.estimated_value > 0;

    const noDataAlert = document.getElementById('no-data-alert');
    const valueRangeDisplay = document.getElementById('value-range');
    if (noDataAlert && valueRangeDisplay) {
        noDataAlert.style.display = hasData ? 'none' : 'flex';
        valueRangeDisplay.style.display = hasData ? 'block' : 'none';
    }

    const confidenceText = document.getElementById('confidence-text');
    if (confidenceText) {
        if (hasData && appraisal.confidence_level) {
            const stars = '⭐'.repeat(appraisal.reliability_stars || 3);
            confidenceText.textContent = `${stars} (${appraisal.confidence_level}%)`;
        } else {
            confidenceText.textContent = t('appraisal-res-confidence-low');
        }
    }

    const isTestMode = appraisal.reasoning?.includes('TEST MODE');

    if (isTestMode) {
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
        animateValue("res-min", 0, appraisal.estimated_range_min || 0, 500);
        animateValue("res-max", 0, appraisal.estimated_range_max || 0, 500);
        animateValue("res-sqm", 0, appraisal.avg_price_sqm || 0, 500);

        if (metrics && Object.keys(metrics).length > 0 && hasData) {
            animateValue("res-rent", 0, metrics.monthly_rent || 0, 500);
            animateValue("res-yield", 0, metrics.cap_rate || 0, 500, true);
            animateValue("res-cap-rate", 0, metrics.cap_rate || 0, 500, true);
            animateValue("res-roi", 0, metrics.roi || 0, 500, true);
            animateValue("res-coc", 0, metrics.cash_on_cash_return || 0, 500, true);
        }
    }

    submitBtn.innerHTML = `<span data-translate="appraisal-cta">${t('appraisal-cta')}</span> <i class="ph ph-arrow-right"></i>`;
    submitBtn.disabled = false;
}
