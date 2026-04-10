/** Kazakhstan phone: digits only for API, formatted for display (+7 XXX XXX XXXX). */

export function formatPhoneInput(value: string): string {
  let cleaned = value.replace(/\D/g, "");
  if (cleaned.startsWith("8")) {
    cleaned = "7" + cleaned.slice(1);
  }
  if (!cleaned.startsWith("7") && cleaned.length > 0) {
    cleaned = "7" + cleaned;
  }
  let formatted = "";
  if (cleaned.length > 0) formatted = "+" + cleaned.slice(0, 1);
  if (cleaned.length > 1) formatted += " " + cleaned.slice(1, 4);
  if (cleaned.length > 4) formatted += " " + cleaned.slice(4, 7);
  if (cleaned.length > 7) formatted += " " + cleaned.slice(7, 11);
  return formatted;
}

export function phoneToApiDigits(formatted: string): string {
  return formatted.replace(/\D/g, "");
}

export function isPhoneCompleteForKz(formatted: string): boolean {
  const d = phoneToApiDigits(formatted);
  return d.length >= 11 && d.startsWith("7");
}
