/**
 * Turn a raw phone string into a display/tel pair.
 * Input:  "(202) 224-2523"
 * Output: { display: "(202) 224-2523", tel: "tel:+12022242523" }
 */
export function formatPhone(rawPhone) {
  if (!rawPhone) return null;
  const digits = rawPhone.replace(/\D/g, '');
  return { display: rawPhone, tel: `tel:+1${digits}` };
}
