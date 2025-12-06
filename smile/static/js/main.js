// Smile Shop - JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Ajouter au panier avec AJAX
    const addToCartForms = document.querySelectorAll('form[action*="add"]');
    addToCartForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            // Pour une meilleure UX, on peut faire l'ajout en AJAX
            // Pour l'instant on laisse le comportement par défaut
        });
    });

    // Animation sur les cartes produits
    const productCards = document.querySelectorAll('.product-card');
    productCards.forEach(card => {
        card.classList.add('fade-in');
    });

    // Auto-hide des alertes après 5 secondes
    const alerts = document.querySelectorAll('.alert:not(.alert-info)');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.classList.remove('show');
            setTimeout(() => alert.remove(), 150);
        }, 5000);
    });
});

// Fonction pour mettre à jour le compteur du panier
function updateCartCount(count) {
    const badge = document.querySelector('.cart-badge');
    if (badge) {
        if (count > 0) {
            badge.textContent = count;
            badge.style.display = 'inline';
        } else {
            badge.style.display = 'none';
        }
    }
}
