"""
QR Code generation utility for patient identification.
"""
import qrcode
import io
import base64
from PIL import Image


def generate_patient_qr(patient_id: str, patient_name: str = None) -> bytes:
    """
    Generate a QR code for patient identification.
    
    Args:
        patient_id: The unique patient identifier.
        patient_name: Optional patient name to include.
        
    Returns:
        PNG image bytes of the QR code.
    """
    # Create QR data payload
    qr_data = f"HMS-PATIENT:{patient_id}"
    if patient_name:
        qr_data += f"|{patient_name}"
    
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    # Create image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to bytes
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    return buffer.getvalue()


def generate_qr_base64(patient_id: str, patient_name: str = None) -> str:
    """
    Generate a base64-encoded QR code for embedding in web pages.
    
    Args:
        patient_id: The unique patient identifier.
        patient_name: Optional patient name to include.
        
    Returns:
        Base64-encoded PNG image string.
    """
    qr_bytes = generate_patient_qr(patient_id, patient_name)
    return base64.b64encode(qr_bytes).decode('utf-8')


def decode_patient_qr(qr_data: str) -> dict:
    """
    Decode a patient QR code data string.
    
    Args:
        qr_data: The scanned QR code data.
        
    Returns:
        Dictionary with patient_id and optionally patient_name.
    """
    if not qr_data.startswith("HMS-PATIENT:"):
        raise ValueError("Invalid HMS QR code format")
    
    data = qr_data.replace("HMS-PATIENT:", "")
    parts = data.split("|")
    
    result = {"patient_id": parts[0]}
    if len(parts) > 1:
        result["patient_name"] = parts[1]
    
    return result
