/**
 * RESTAURANT & CAFÉ MANAGEMENT SYSTEM
 * Frontend JavaScript Controller (script.js)
 * Handles client-side interactivity, live cart calculations, filters, and validations
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Initialize Auto-dismiss alerts after 5 seconds
    initFlashAlerts();

    // 2. Initialize Menu Filter & Live Search
    initMenuFilter();

    // 3. Initialize Password Match Validation
    initRegisterValidation();

    // 4. Initialize Reservation Date constraints
    initReservationConstraints();
});

/**
 * Auto dismiss Bootstrap flash alerts smoothly after 5 seconds
 */
function initFlashAlerts() {
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(alert => {
        setTimeout(() => {
            try {
                const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
                bsAlert.close();
            } catch (e) {
                alert.style.display = 'none';
            }
        }, 5000);
    });
}

/**
 * Menu Live Search and Category Quick Filtering
 */
function initMenuFilter() {
    const searchInput = document.getElementById('menuSearchInput');
    const vegOnlyCheckbox = document.getElementById('vegOnlyFilter');
    const foodItems = document.querySelectorAll('.menu-item-col');

    if (!searchInput && !vegOnlyCheckbox) return;

    function applyFilters() {
        const query = (searchInput ? searchInput.value.toLowerCase().trim() : '');
        const vegOnly = vegOnlyCheckbox ? vegOnlyCheckbox.checked : false;
        let visibleCount = 0;

        foodItems.forEach(item => {
            const name = item.getAttribute('data-name')?.toLowerCase() || '';
            const desc = item.getAttribute('data-desc')?.toLowerCase() || '';
            const isVeg = item.getAttribute('data-veg') === 'true';

            const matchesSearch = name.includes(query) || desc.includes(query);
            const matchesVeg = vegOnly ? isVeg : true;

            if (matchesSearch && matchesVeg) {
                item.style.display = 'block';
                visibleCount++;
            } else {
                item.style.display = 'none';
            }
        });

        const noResultsMsg = document.getElementById('noResultsMessage');
        if (noResultsMsg) {
            noResultsMsg.style.display = visibleCount === 0 ? 'block' : 'none';
        }
    }

    if (searchInput) {
        searchInput.addEventListener('input', applyFilters);
    }
    if (vegOnlyCheckbox) {
        vegOnlyCheckbox.addEventListener('change', applyFilters);
    }
}

/**
 * Customer Registration Validation
 */
function initRegisterValidation() {
    const regForm = document.getElementById('registrationForm');
    if (!regForm) return;

    regForm.addEventListener('submit', (e) => {
        const pass = document.getElementById('regPassword').value;
        const confirmPass = document.getElementById('regConfirmPassword').value;
        const phone = document.getElementById('regPhone').value.trim();

        if (pass !== confirmPass) {
            e.preventDefault();
            alert('Passwords do not match! Please check and re-enter.');
            document.getElementById('regConfirmPassword').focus();
            return false;
        }

        if (pass.length < 6) {
            e.preventDefault();
            alert('Password must be at least 6 characters long.');
            document.getElementById('regPassword').focus();
            return false;
        }

        // Simple 10-digit phone number check
        const cleanPhone = phone.replace(/[^0-9]/g, '');
        if (cleanPhone.length < 10) {
            e.preventDefault();
            alert('Please enter a valid phone number (at least 10 digits).');
            document.getElementById('regPhone').focus();
            return false;
        }
    });
}

/**
 * Reservation Date constraint: Prevent selecting past dates
 */
function initReservationConstraints() {
    const resDateInput = document.getElementById('reservation_date');
    if (!resDateInput) return;

    // Set today as minimum date
    const today = new Date().toISOString().split('T')[0];
    resDateInput.setAttribute('min', today);
}

/**
 * Confirmation dialog for dangerous actions (e.g. deleting food item)
 */
function confirmAction(message) {
    return confirm(message || 'Are you sure you want to proceed with this action?');
}

/**
 * Printable invoice trigger
 */
function printInvoice() {
    window.print();
}

