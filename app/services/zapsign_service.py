import os
import base64
import requests
from app.config.settings import settings

def send_contract_to_zapsign(file_path: str, client_name: str, client_email: str) -> dict:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"❌ File not found: {file_path}")

    url = f"{settings.ZAPSIGN_URL}docs/"
    base_filename = os.path.basename(file_path)

    with open(file_path, 'rb') as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')

    payload = {
        "api_token": settings.ZAPSIGN_API_KEY,
        "name": base_filename,
        "base64_pdf": base64_pdf,
        "lang": "pt-br",
        "signers": [
            {
                "name": client_name,
                "email": client_email,
                "send_automatic_email": False
            },
            {
                "name": "Alberto & Tadeu Advogados",
                "email": "contato@albertoetadeu.com",
                "send_automatic_email": False
            }
        ]
    }

    print(f"📤 [ZAPSIGN] Sending contract to: {client_name}")

    response = None
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        response_data = response.json()
        print(f"✅ [ZAPSIGN] Contract sent! ID: {response_data.get('open_id')}")
        return response_data
    except requests.exceptions.RequestException as e:
        print(f"❌ [ZAPSIGN] Error with communication with API: {e}")
        if response is not None:
            print(f"📋 Response content: {response.text}")
        raise
