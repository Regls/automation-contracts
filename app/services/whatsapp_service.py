import requests
from app.config.settings import settings

def send_whatsapp_notification(number: str, client_name: str, sign_url: str) -> dict:
    """Notify via Evolution API that contract is ready to sign"""

    clean_number = "".join(filter(str.isdigit, number))

    url = f"{settings.EVOLUTION_API_URL}/message/sendText/{settings.EVOLUTION_INSTANCE}"

    headers = {
        "Content-Type": "application/json",
        "apikey": settings.EVOLUTION_API_KEY
    }

    message = f"""⚖️ *Alberto & Tadeu Advogados Associados*\n\n
Olá {client_name}!
Seu contrato está pronto para assinatura digital.

Clique no link abaixo para assinar:
{sign_url}

Atenciosamente,
Equipe de Contratos
    """

    payload = {
        "number": clean_number,
        "text": message,
        "options": {
            "delay": 1200,
            "presence": "composing",
            "linkPreview": True
        }
    }

    print(f"📤 Sending WhatsApp message to: {client_name} ({clean_number})")

    response = None
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        print(f"✅ [WHATSAPP] WhatsApp message sent successfully to {client_name}!")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ [WHATSAPP] Error communicating with Evolution API: {e}")
        if response is not None:
            print(f"📋 Evolution API Response: {response.text}")
        return {}
    
