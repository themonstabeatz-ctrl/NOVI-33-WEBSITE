/**
 * ✅ NORMALIZE PRICING UTILITY
 * 
 * Backend može slati snake_case ili camelCase polja.
 * Ova funkcija normalizuje SVE varijante u jedinstveni format.
 * 
 * Polja koja se normalizuju:
 * - original_price / originalPrice / price
 * - final_price / finalPrice
 * - discount_percent / discountPercentage / discount_percentage / discount
 * - has_discount / hasDiscount
 */

export function normalizePricing(item) {
  if (!item) return item;
  
  // ✅ Normalizuj original_price
  const original_price = Number(
    item.original_price ?? 
    item.originalPrice ?? 
    item.metadata?.original_price ??
    item.price ?? 
    0
  );
  
  // ✅ Normalizuj discount_percent
  const discount_percent = Number(
    item.discount_percent ?? 
    item.discountPercentage ?? 
    item.discount_percentage ??
    item.metadata?.discount_applied ??
    item.discount ?? 
    0
  );
  
  // ✅ Normalizuj final_price
  const final_price = Number(
    item.final_price ?? 
    item.finalPrice ?? 
    item.metadata?.final_price ??
    original_price
  );
  
  // ✅ Izračunaj has_discount
  const has_discount = Boolean(
    item.has_discount ?? 
    item.hasDiscount ?? 
    (discount_percent > 0 && final_price < original_price)
  );
  
  return {
    ...item,
    original_price,
    final_price,
    discount_percent,
    has_discount,
  };
}

/**
 * ✅ Batch normalize - za liste servisa
 */
export function normalizeServiceList(data) {
  const items = Array.isArray(data) ? data : (data?.items || []);
  return items.map(normalizePricing);
}

export default normalizePricing;
