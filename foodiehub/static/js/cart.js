/* cart.js — quantity +/- and remove handlers on the cart page */

async function updateCartQty(cartId, delta) {
  const qtyEl = document.getElementById(`qty-${cartId}`);
  if (!qtyEl) return;
  let newQty = parseInt(qtyEl.textContent, 10) + delta;

  if (newQty <= 0) {
    removeCartItem(cartId);
    return;
  }

  const formData = new FormData();
  formData.append('cart_id', cartId);
  formData.append('quantity', newQty);

  try {
    const res = await fetch('/cart/update', { method: 'POST', body: formData });
    const data = await res.json();
    if (data.success) {
      qtyEl.textContent = newQty;
      applyTotals(data.totals);
      updateCartBadge(data.cart_count);
    }
  } catch (err) {
    showToast('Could not update quantity.');
  }
}

async function removeCartItem(cartId) {
  const formData = new FormData();
  formData.append('cart_id', cartId);

  try {
    const res = await fetch('/cart/remove', {
      method: 'POST',
      headers: { 'X-Requested-With': 'XMLHttpRequest' },
      body: formData,
    });
    const data = await res.json();
    if (data.success) {
      const row = document.querySelector(`.cart-item-row[data-cart-id="${cartId}"]`);
      if (row) row.remove();
      applyTotals(data.totals);
      updateCartBadge(data.cart_count);
      showToast('Item removed from cart.');

      if (data.item_count === 0) {
        setTimeout(() => window.location.reload(), 500);
      }
    }
  } catch (err) {
    showToast('Could not remove item.');
  }
}

function applyTotals(totals) {
  const fmt = (n) => `₹${Number(n).toFixed(2)}`;
  const subtotalEl = document.getElementById('sumSubtotal');
  const deliveryEl = document.getElementById('sumDelivery');
  const taxEl = document.getElementById('sumTax');
  const discountEl = document.getElementById('sumDiscount');
  const totalEl = document.getElementById('sumTotal');

  if (subtotalEl) subtotalEl.textContent = fmt(totals.subtotal);
  if (deliveryEl) deliveryEl.textContent = fmt(totals.delivery_fee);
  if (taxEl) taxEl.textContent = fmt(totals.tax);
  if (discountEl) discountEl.textContent = `-${fmt(totals.discount)}`;
  if (totalEl) totalEl.textContent = fmt(totals.grand_total);
}
