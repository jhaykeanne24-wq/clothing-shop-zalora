// Add to Cart Functionality
function addToCart(productId, quantity = 1) {
    fetch('/add-to-cart', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            product_id: productId,
            quantity: quantity
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification(data.msg, 'success');
            updateCartCount(data.cart_count);
        } else {
            showNotification(data.msg, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Error adding to cart', 'error');
    });
}

// Remove from Cart
function removeFromCart(productId) {
    if (confirm('Are you sure you want to remove this item?')) {
        fetch(`/remove-from-cart/${productId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            }
        })
        .catch(error => console.error('Error:', error));
    }
}

// Show Notification
function showNotification(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 1000; min-width: 300px;';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertDiv);
    
    setTimeout(() => {
        alertDiv.remove();
    }, 4000);
}

// Update Cart Count
function updateCartCount(count) {
    const cartBadge = document.querySelector('.navbar-nav .badge');
    if (cartBadge) {
        cartBadge.textContent = count;
    }
}

// Format Currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

// Search Functionality
const searchInput = document.querySelector('input[name="search"]');
if (searchInput) {
    searchInput.addEventListener('input', function() {
        // Debounce search
        clearTimeout(this.searchTimeout);
        this.searchTimeout = setTimeout(() => {
            // Auto-submit form or perform search
        }, 300);
    });
}

// Add to Cart Button Event Listeners
document.querySelectorAll('.add-to-cart').forEach(button => {
    button.addEventListener('click', function(e) {
        e.preventDefault();
        const productId = this.dataset.productId;
        const quantityInput = document.getElementById('quantity');
        const quantity = quantityInput ? parseInt(quantityInput.value) : 1;
        
        addToCart(productId, quantity);
    });
});

// Remove from Cart Button Event Listeners
document.querySelectorAll('.remove-from-cart').forEach(button => {
    button.addEventListener('click', function(e) {
        e.preventDefault();
        const productId = this.dataset.productId;
        removeFromCart(productId);
    });
});

// Filter Products
const filterForm = document.querySelector('form');
if (filterForm) {
    const categorySelect = filterForm.querySelector('select[name="category"]');
    const searchInput = filterForm.querySelector('input[name="search"]');
    
    if (categorySelect) {
        categorySelect.addEventListener('change', () => {
            filterForm.submit();
        });
    }
}

// Form Validation
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return true;
    
    const inputs = form.querySelectorAll('input[required], textarea[required], select[required]');
    let isValid = true;
    
    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.classList.add('is-invalid');
            isValid = false;
        } else {
            input.classList.remove('is-invalid');
        }
    });
    
    return isValid;
}

// Add Bootstrap Validation
const forms = document.querySelectorAll('form');
forms.forEach(form => {
    form.addEventListener('submit', function(e) {
        if (!this.checkValidity()) {
            e.preventDefault();
            e.stopPropagation();
        }
        this.classList.add('was-validated');
    }, false);
});

// Quantity Input Handler
const quantityInputs = document.querySelectorAll('input[type="number"]');
quantityInputs.forEach(input => {
    input.addEventListener('change', function() {
        if (this.value < 1) {
            this.value = 1;
        }
        const maxStock = this.getAttribute('max');
        if (maxStock && this.value > maxStock) {
            this.value = maxStock;
            showNotification('Maximum stock exceeded', 'warning');
        }
    });
});

// Toggle Password Visibility
function togglePasswordVisibility(inputId) {
    const input = document.getElementById(inputId);
    if (input) {
        input.type = input.type === 'password' ? 'text' : 'password';
    }
}

// Smooth Scroll
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    // Add animation to elements on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -100px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);
    
    document.querySelectorAll('.product-card').forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        observer.observe(card);
    });
});

// API Error Handler
function handleError(error) {
    console.error('Error:', error);
    showNotification('An error occurred. Please try again.', 'error');
}

// Local Storage for Cart (fallback)
const cart = {
    get: () => JSON.parse(localStorage.getItem('cart')) || [],
    set: (items) => localStorage.setItem('cart', JSON.stringify(items)),
    add: (item) => {
        const items = cart.get();
        const existing = items.find(i => i.product_id === item.product_id);
        if (existing) {
            existing.quantity += item.quantity;
        } else {
            items.push(item);
        }
        cart.set(items);
    },
    remove: (productId) => {
        let items = cart.get();
        items = items.filter(i => i.product_id !== productId);
        cart.set(items);
    },
    clear: () => cart.set([])
};

// Console greeting
console.log('%cWelcome to Fashion Store', 'font-size: 20px; font-weight: bold; color: #007bff;');
console.log('%cVersion 1.0.0', 'color: #666;');
