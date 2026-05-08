/**
 * 🔐 SPA CARD IDs - Centralized constants for card-level discounts
 * 
 * These IDs map to backend /api/spa/cards endpoints
 * Used in /api/spa/quote requests to apply card-level discounts
 * 
 * ⚠️ DO NOT hardcode card_id in components - always use these constants!
 */

export const SPA_CARD_IDS = {
  // SPA Rituals (main packages)
  SILKY_BODY_RITUAL: "silky_body_ritual",
  GENTLE_TOUCH_RITUAL: "gentle_touch_ritual",
  DEEP_RENEWAL_RITUAL: "deep_renewal_ritual",

  // Herbal Rituals (fixed-price packages)
  SILKY_HERBAL_COMPRESS_RITUAL: "silky_herbal_compress_ritual",
  THAI_HERBAL_COMPRESS_RITUAL: "thai_herbal_compress_ritual",
  AROMA_STONE_HARMONY_RITUAL: "aroma_stone_harmony_ritual",

  // SPA Zone card (zone-only booking)
  SPA_ZONE: "spa_zone",

  // Special occasions / Couple packages
  ROMANTIC_COUPLE_PACKAGE: "romantic_couple_package",
  ROMANTIC_PEELING_COUPLE_PACKAGE: "romantic_peeling_couple_package",
};

/**
 * 🔐 Backend Service IDs for each ritual
 * These UUIDs come from /api/spa/services endpoint
 */
export const BASE_SERVICE_IDS = {
  // Main SPA Rituals
  SILKY_BODY_RITUAL: "ed3d9995-e195-4e56-8041-3459d3ecd324",
  GENTLE_TOUCH_RITUAL: "3308333f-de1a-40a5-b33a-6acc171bc538",
  DEEP_RENEWAL_RITUAL: "b4067c22-e4c0-4db7-aa7a-b6b6d396e27a",
  
  // Herbal Rituals
  SILKY_HERBAL_COMPRESS_RITUAL: "ce2e8ccd-e95c-41b2-bae9-0d9b0f53cc2f",
  THAI_HERBAL_COMPRESS_RITUAL: "a406a2b4-a2ee-46af-9897-d20f71534a22",
  AROMA_STONE_HARMONY_RITUAL: "f8cdfaac-9414-4eeb-8136-0d9d3d0e73b8",
  
  // Face Massage addon
  FACE_MASSAGE: "b398a25e-4f70-4060-80ac-e080fc34a0ef",
  
  // SPA Zone services
  SAUNA_15: "7d46da23-a15a-4836-8db5-04d748cd6b72",
  SAUNA_30: "9bcb2fa6-4474-48be-93bd-72bea64a9807",
  STEAM_15: "876dff5c-4a13-4f5d-a4ff-b431f42b81e4",
  STEAM_30: "e00a0411-30fb-4a5e-87ef-32509bd1890e",
  JACUZZI_30: "af7458f2-6c40-4957-8871-347438e9ec57",
  JACUZZI_60: "ef4206ac-372c-40d9-9cf8-1dcaf1a42979",
  
  // Romantic packages
  ROMANTIC_COUPLE: "0431d7d9-c8cd-4392-bbed-f91298ace763",
  ROMANTIC_PEELING: "80cd6f57-da53-4558-8641-9f8589b0726f",
};

/**
 * Map frontend package IDs to backend card IDs
 * Used to look up which card_id to send in quote request
 * 
 * ⚠️ MUST cover ALL package codes used in frontend!
 */
export const PACKAGE_TO_CARD_MAP = {
  // Main SPA Rituals (from SPA_PACKAGES array)
  "SPA1": SPA_CARD_IDS.SILKY_BODY_RITUAL,
  "SPA2": SPA_CARD_IDS.GENTLE_TOUCH_RITUAL,
  "SPA3": SPA_CARD_IDS.DEEP_RENEWAL_RITUAL,
  
  // Herbal packages (from HERBAL_COMPRESS_CARDS)
  "SPA_HC_1": SPA_CARD_IDS.SILKY_HERBAL_COMPRESS_RITUAL,
  "SPA_HC_2": SPA_CARD_IDS.THAI_HERBAL_COMPRESS_RITUAL,
  "SPA_HC_3": SPA_CARD_IDS.AROMA_STONE_HARMONY_RITUAL,
  
  // Zone only (SPA_ZONE_ONLY.id = "SPAZONE")
  "SPAZONE": SPA_CARD_IDS.SPA_ZONE,
  "SPA_ZONE_ONLY": SPA_CARD_IDS.SPA_ZONE, // alias
  
  // Couple packages
  "ROMANTIC_COUPLE": SPA_CARD_IDS.ROMANTIC_COUPLE_PACKAGE,
  "ROMANTIC_PEELING": SPA_CARD_IDS.ROMANTIC_PEELING_COUPLE_PACKAGE,
};

/**
 * Map frontend package IDs to default base service_ids
 * Used for initial quote call on mount (before user selects options)
 */
export const PACKAGE_TO_BASE_SERVICE_IDS = {
  "SPA1": [BASE_SERVICE_IDS.SILKY_BODY_RITUAL],
  "SPA2": [BASE_SERVICE_IDS.GENTLE_TOUCH_RITUAL],
  "SPA3": [BASE_SERVICE_IDS.DEEP_RENEWAL_RITUAL],
  
  "SPA_HC_1": [BASE_SERVICE_IDS.SILKY_HERBAL_COMPRESS_RITUAL],
  "SPA_HC_2": [BASE_SERVICE_IDS.THAI_HERBAL_COMPRESS_RITUAL],
  "SPA_HC_3": [BASE_SERVICE_IDS.AROMA_STONE_HARMONY_RITUAL],
  
  // Zone only doesn't have base service - it's just zone selections
  "SPAZONE": [],
  "SPA_ZONE_ONLY": [],
  
  // Romantic packages
  "ROMANTIC_COUPLE": [BASE_SERVICE_IDS.ROMANTIC_COUPLE],
  "ROMANTIC_PEELING": [BASE_SERVICE_IDS.ROMANTIC_PEELING],
};

export default SPA_CARD_IDS;
