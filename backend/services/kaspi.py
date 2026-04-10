"""Сервис генерации QR-кода для оплаты через Kaspi"""
import qrcode
import io
import base64
from urllib.parse import quote

from config import KASPI_PHONE


def generate_kaspi_link(amount: float, comment: str) -> str:
    """Генерирует ссылку для оплаты через Kaspi"""
    # Очищаем номер телефона от лишних символов
    phone = KASPI_PHONE.replace("+", "").replace(" ", "").replace("-", "")

    # URL-кодируем комментарий
    encoded_comment = quote(comment)

    # Формируем Kaspi deep link
    kaspi_link = f"https://kaspi.kz/pay?phone={phone}&amount={int(amount)}&comment={encoded_comment}"

    return kaspi_link


def generate_qr_base64(data: str) -> str:
    """Генерирует QR-код и возвращает его в формате base64"""
    # Создаём QR-код
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    # Создаём изображение
    img = qr.make_image(fill_color="black", back_color="white")

    # Конвертируем в base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)

    return base64.b64encode(buffer.getvalue()).decode('utf-8')


def generate_kaspi_qr(amount: float, booking_id: int) -> tuple[str, str]:
    """
    Генерирует ссылку и QR-код для оплаты через Kaspi

    Args:
        amount: Сумма платежа
        booking_id: ID записи для формирования комментария

    Returns:
        tuple: (kaspi_link, qr_code_base64)
    """
    comment = f"Booking{booking_id}"

    kaspi_link = generate_kaspi_link(amount, comment)
    qr_base64 = generate_qr_base64(kaspi_link)

    return kaspi_link, qr_base64
