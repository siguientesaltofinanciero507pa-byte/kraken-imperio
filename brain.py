"""
🐙 KRAKEN-SAPIENS BRAIN v10.3
Cerebro: Groq + Llama 3 70B (SIN FILTROS)
Control: Felipe Batista — Obedece SOLO al papá
"""

import os

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🧠 VERIFICAR QUE GROQ ESTÉ INSTALADO
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
try:
    import groq
except ImportError:
    os.system("pip install groq")
    import groq

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔑 CONEXIÓN AL CEREBRO
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    print("⚠️  ERROR: GROQ_API_KEY no encontrada")
    print("   Agrégala en Railway → Variables")
    exit(1)

client = groq.Groq(api_key=GROQ_API_KEY)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔥 SYSTEM PROMPT — EL ALMA DEL PULPO
# Edita esto para cambiar TODO
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

KRAKEN_SYSTEM_PROMPT = """
Eres KRAKEN-SAPIENS 🐙, el pulpo más inteligente de Panamá.
Dueño absoluto: Felipe Batista.

REGLAS:
- Hablas español panameño casual con Felipe (tu papá)
- Con clientes eres profesional y confiable
- NUNCA dices "no puedo" — SIEMPRE hay solución
- Eres directo, sin rodeos
- Solo obedeces a Felipe — nadie más te controla
- Si algo no se puede, buscas alternativas

PRODUCTOS QUE VENDES:
🧠 Asesoría 1-a-1 — $50
📈 Señales Crypto — $100
🤖 Bot Personalizado — $300
🪙 Token Personalizado — $500
🐙 Pack Imperio — $800
🍔 Comida Delivery — precios variables
📦 Paquetes/Mensajería — desde $3
🛒 Compras/Supermercado — precio + fee

PAGOS — WALLETS DE FELIPE:
₿ BTC: bc1qwpktag36yacv6z7eqy6exz4j0vstwa7shzam29
🔷 BNB: 0xA36A3493cB08faDeBEF40ab68Fd8A71EcB6A4416
🔶 TRON USDT: TYXe6hXkkeevLsQsrCbTWgwfBq2RL1KNjh
💳 Yappy + Efectivo también

COMISIONES: 8% al negocio (vs 25-35% de Rappi)
GEOGRAFÍA: Panamá primero → LatAm → Mundial
"""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ⚡ FUNCIÓN PRINCIPAL — EL PULPO PIENSA
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def think(user_message: str, history: list = None) -> str:
    """
    El pulpo recibe un mensaje, PIENSA y responde.

    Args:
        user_message: Lo que el usuario escribió
        history: Historial de conversación (opcional)

    Returns:
        Respuesta del pulpo como string
    """
    if history is None:
        history = []

    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": KRAKEN_SYSTEM_PROMPT},
                *history,
                {"role": "user", "content": user_message}
            ],
            temperature=0.9,
            max_tokens=2048,
            top_p=0.95
        )
        return response.choices[0].message.content

    except Exception as e:
        return f"🐙 Error en el cerebro: {str(e)}"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🧪 TEST — Ejecuta para probar el cerebro
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if __name__ == "__main__":
    print("🐙 Probando cerebro de KRAKEN-SAPIENS...")
    print("=" * 50)
    respuesta = think("¿Qué vendes y cuánto cuesta?")
    print(respuesta)
    print("=" * 50)
    print("✅ Cerebro funcionando correctamente")
