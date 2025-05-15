import base64
import random
import string

def encrypt(plain_text):
    encoded = base64.b64encode(plain_text.encode()).decode()
    noise = ''.join(random.choices(string.ascii_letters + string.digits, k=4))
    pos = random.randint(1, len(encoded) - 1)
    obfuscated = encoded[:pos] + noise + encoded[pos:]
    result = f"{pos:02d}{obfuscated}"
    return result

def decrypt(obfuscated_text):
    pos = int(obfuscated_text[:2])
    cleaned = obfuscated_text[2:pos+2] + obfuscated_text[pos+6:]
    decoded = base64.b64decode(cleaned.encode()).decode()
    return decoded

