/* main.js — global helpers used across pages: toasts, add-to-cart, favorites */

function showToast(message) {
  const toast = document.getElementById('toast');
  if (!toast) return;
  toast.textContent = message;
  toast.classList.add('show');
  clearTimeout(window.__toastTimer);
  window.__toastTimer = setTimeout(() => toast.classList.remove('show'), 2200);
}

function updateCartBadge(count) {
  document.querySelectorAll('.cart-badge').forEach(el => {
    el.textContent = count;
    el.style.display = count > 0 ? 'flex' : 'none';
  });
  // if no badge existed yet (count was 0), we simply leave it; page reload will render it.
}

async function addToCart(foodId, btnEl) {
  try {
    if (btnEl) {
      btnEl.disabled = true;
      btnEl.textContent = 'Adding...';
    }
    const formData = new FormData();
    formData.append('food_id', foodId);
    formData.append('quantity', 1);

    const res = await fetch('/cart/add', {
      method: 'POST',
      headers: { 'X-Requested-With': 'XMLHttpRequest' },
      body: formData,
    });
    const data = await res.json();

    if (data.success) {
      showToast(data.message || 'Added to cart!');
      updateCartBadge(data.cart_count);
    } else {
      showToast(data.message || 'Could not add item.');
    }
  } catch (err) {
    showToast('Something went wrong. Please try again.');
  } finally {
    if (btnEl) {
      btnEl.disabled = false;
      btnEl.textContent = '+ Add to Cart';
    }
  }
}

async function addToCartWithQty(foodId, quantity, onSuccess) {
  try {
    const formData = new FormData();
    formData.append('food_id', foodId);
    formData.append('quantity', quantity);
    const res = await fetch('/cart/add', {
      method: 'POST',
      headers: { 'X-Requested-With': 'XMLHttpRequest' },
      body: formData,
    });
    const data = await res.json();
    if (data.success) {
      showToast(data.message || 'Added to cart!');
      updateCartBadge(data.cart_count);
      if (onSuccess) onSuccess();
    } else {
      showToast(data.message || 'Could not add item.');
    }
  } catch (err) {
    showToast('Something went wrong. Please try again.');
  }
}

async function toggleFavorite(foodId, btnEl) {
  try {
    const formData = new FormData();
    formData.append('food_id', foodId);
    const res = await fetch('/favorite/toggle', {
      method: 'POST',
      headers: { 'X-Requested-With': 'XMLHttpRequest' },
      body: formData,
    });
    const data = await res.json();
    if (data.success && btnEl) {
      btnEl.textContent = data.is_favorite ? '❤️' : '🤍';
      showToast(data.is_favorite ? 'Added to favorites!' : 'Removed from favorites.');
    }
  } catch (err) {
    showToast('Could not update favorites.');
  }
}

// Auto-dismiss flash messages after a few seconds
document.addEventListener('DOMContentLoaded', () => {
  const flashes = document.querySelectorAll('.flash');
  flashes.forEach((el, i) => {
    setTimeout(() => {
      el.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
      el.style.opacity = '0';
      el.style.transform = 'translateX(30px)';
      setTimeout(() => el.remove(), 400);
    }, 6000 + i * 300);
  });
});
