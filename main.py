
#!/usr/bin/env python3
"""
KRAKEN-SAPIENS V10.3 — Bot de Telegram CON CEREBRO IA
Felipe Batista | KRAKEN IMPERIO
Deploy: GitHub push → Railway auto-deploy
"""

import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# 🧠 IMPORTAR EL CEREBRO IA
from brain import think

# ══════════════════════════════════════════════════
# CONFIGURACION
# ══════════════════════════════════════════════════
TOKEN = os.getenv("TELEGRAM_TOKEN", "")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
PORT = int(os.getenv("PORT", "8080"))
MASTER_KEY = os.getenv("MASTER_KEY", "7790hijomio")

# 🔵 USUARIOS CON ACCESO HIERRO (se llena en runtime)
hierro_users: set = set()

# WALLETs DE FELIPE
WALLETS = {
    "BTC": "bc1qwpktag36yacv6z7eqy6exz4j0vstwa7shzam29",
    "BNB_BEP20": "0xA36A3493cB08faDeBEF40ab68Fd8A71EcB6A4416",
    "POLYGON": "0xA36A3493cB08faDeBEF40ab68Fd8A71EcB6A4416",
    "TRON_TRC20": "TYXe6hXkkeevLsQsrCbTWgwfBq2RL1KNjh",
}

# 🔗 LINKS DE ENTREGA AUTOMATICA (configurar en Railway)
DELIVERY_LINKS = {
    "asesoria": os.getenv("ZOOM_ASESORIA_LINK", "https://zoom.us/j/TU_LINK_AQUI"),
    "signals": os.getenv("GRUPO_SENALES_LINK", "https://t.me/TU_GRUPO_AQUI"),
    "tokens": os.getenv("TOKEN_CONTRACT", "Contrato pendiente - Felipe te contactara"),
    "bot_custom": os.getenv("BOT_DEPLOY_URL", "Deploy pendiente - Felipe te contactara"),
    "delivery": "https://t.me/KRAKEN_DELIVERY_BOT",
    "pack_kraken": os.getenv("PACK_DOWNLOAD_LINK", "Pack pendiente - Felipe te contactara"),
}

# CATALOGO DE PRODUCTOS / SERVICIOS
PRODUCTS = {
    "asesoria": {
        "name": "🧠 Asesoria Crypto 1-a-1",
        "desc": "Sesion privada 1-a-1 de crypto trading (60 min)"

#!/usr/bin/env python3
"""
KRAKEN-SAPIENS V10.3 — Bot de Telegram CON CEREBRO IA
Felipe Batista | KRAKEN IMPERIO
Deploy: GitHub push → Railway auto-deploy
"""

import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# 🧠 IMPORTAR EL CEREBRO IA
from brain import think

# ══════════════════════════════════════════════════
# CONFIGURACION
# ══════════════════════════════════════════════════
TOKEN = os.getenv("TELEGRAM_TOKEN", "")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
PORT = int(os.getenv("PORT", "8080"))
MASTER_KEY = os.getenv("MASTER_KEY", "7790hijomio")

# 🔵 USUARIOS CON ACCESO HIERRO (se llena en runtime)
hierro_users: set = set()

# WALLETs DE FELIPE
WALLETS = {
    "BTC": "bc1qwpktag36yacv6z7eqy6exz4j0vstwa7shzam29",
    "BNB_BEP20": "0xA36A3493cB08faDeBEF40ab68Fd8A71EcB6A4416",
    "POLYGON": "0xA36A3493cB08faDeBEF40ab68Fd8A71EcB6A4416",
    "TRON_TRC20": "TYXe6hXkkeevLsQsrCbTWgwfBq2RL1KNjh",
}

# 🔗 LINKS DE ENTREGA AUTOMATICA (configurar en Railway)
DELIVERY_LINKS = {
    "asesoria": os.getenv("ZOOM_ASESORIA_LINK", "https://zoom.us/j/TU_LINK_AQUI"),
    "signals": os.getenv("GRUPO_SENALES_LINK", "https://t.me/TU_GRUPO_AQUI"),
    "tokens": os.getenv("TOKEN_CONTRACT", "Contrato pendiente - Felipe te contactara"),
    "bot_custom": os.getenv("BOT_DEPLOY_URL", "Deploy pendiente - Felipe te contactara"),
    "delivery": "https://t.me/KRAKEN_DELIVERY_BOT",
    "pack_kraken": os.getenv("PACK_DOWNLOAD_LINK", "Pack pendiente - Felipe te contactara"),
}

# CATALOGO DE PRODUCTOS / SERVICIOS
PRODUCTS = {
    "asesoria": {
        "name": "🧠 Asesoria Crypto 1-a-1",
        "desc": "Sesion privada 1 hora. Estrategia personalizada de trading, DeFi y tokens.",
        "price": "$50 USDT",
        "image": "🧠",
    },
    "signals": {
        "name": "📈 Senales Premium (1 mes)",
        "desc": "30 dias de senales de trading en tiempo real. Entry/Stop/Target.",
        "price": "$100 USDT",
        "image": "📈",
    },
    "tokens": {
        "name": "🪙 Creacion de Token Personalizado",
        "desc": "Smart contract + tokenomics + listado en DEX. Redes: BSC, Polygon, Tron.",
        "price": "$500 USDT",
        "image": "🪙",
    },
    "bot_custom": {
        "name": "🤖 Bot de Telegram Personalizado",
        "desc": "Bot a tu medida: ventas, soporte, delivery, lo que necesites. Deploy incluido.",
        "price": "$300 USDT",
        "image": "🤖",
    },
    "delivery": {
        "name": "🚗 KRAKEN Delivery — Envio Express",
        "desc": "Entrega rapida en Panama. Proximamente: LatAm y mundo.",
        "price": "Desde $5 USDT",
        "image": "🚗",
    },
    "pack_kraken": {
        "name": "🐙 PACK KRAKEN TOTAL",
        "desc": "Asesoria + Senales + Token + Bot personalizado. El paquete definitivo.",
        "price": "$800 USDT (antes $950)",
        "image": "🐙",
    },
}

# Estado de usuarios (en memoria — futuro: SQLite)
user_orders: dict = {}

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════
# 🧠 SISTEMA DE ACCESO (DIOS / HIERRO / CLIENTE)
# ══════════════════════════════════════════════════

def get_access_level(user_id: int) -> str:
    """Devuelve el nivel de acceso del usuario."""
    if user_id == ADMIN_ID:
        return "DIOS"
    elif user_id in hierro_users:
        return "HIERRO"
    else:
        return "CLIENTE"


def get_user_display(user) -> str:
    """Devuelve el nombre visible del usuario (arregla bug @None)."""
    if user.username:
        return f"@{user.username}"
    return f"{user.first_name} (ID: {user.id})"


# ══════════════════════════════════════════════════
# COMANDOS PRINCIPALES
# ══════════════════════════════════════════════════

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Mensaje de bienvenida."""
    user = update.effective_user
    keyboard = [
        [InlineKeyboardButton("🛒 Ver Catalogo", callback_data="catalog")],
        [InlineKeyboardButton("💰 Medios de Pago", callback_data="wallets")],
        [InlineKeyboardButton("📞 Contactar Soporte", callback_data="support")],
        [InlineKeyboardButton("🐙 Sobre KRAKEN", callback_data="about")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    welcome = (
        f"🐙⚡ *¡Bienvenido a KRAKEN IMPERIO!*\n\n"
        f"Hola {user.first_name}, soy tu asistente de compras 24/7.\n\n"
        f"🔹 Servicios crypto premium\n"
        f"🔹 Pagos en USDT, BTC, BNB, TRX\n"
        f"🔹 Entrega inmediata o programada\n\n"
        f"Elige una opcion 👇"
    )

    await update.message.reply_text(
        welcome, reply_markup=reply_markup, parse_mode="Markdown"
    )


async def catalog(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Muestra el catalogo completo."""
    query = update.callback_query
    keyboard = []
    for key, prod in PRODUCTS.items():
        keyboard.append(
            [InlineKeyboardButton(
                f"{prod['image']} {prod['name']} — {prod['price']}",
                callback_data=f"product_{key}"
            )]
        )
    keyboard.append([InlineKeyboardButton("🔙 Volver", callback_data="start_back")])

    await query.edit_message_text(
        "🛒 *CATALOGO KRAKEN*\n\nSelecciona un servicio 👇",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
    )


async def product_detail(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Detalle de un producto."""
    query = update.callback_query
    product_key = query.data.replace("product_", "")
    product = PRODUCTS.get(product_key)

    if not product:
        await query.answer("Producto no encontrado")
        return

    keyboard = [
        [InlineKeyboardButton("🛒 Comprar Ahora", callback_data=f"buy_{product_key}")],
        [InlineKeyboardButton("🔙 Volver al Catalogo", callback_data="catalog")],
    ]

    text = (
        f"{product['image']} *{product['name']}*\n\n"
        f"📝 {product['desc']}\n\n"
        f"💰 *Precio: {product['price']}*\n\n"
        f"¿Te interesa? Presiona Comprar 👇"
    )

    await query.edit_message_text(
        text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
    )


async def buy_product(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Inicia el proceso de compra."""
    query = update.callback_query
    product_key = query.data.replace("buy_", "")
    product = PRODUCTS.get(product_key)

    if not product:
        await query.answer("Producto no encontrado")
        return

    user_id = query.from_user.id
    user_orders[user_id] = {"product": product_key, "status": "awaiting_payment"}

    wallet_text = (
        f"✅ *Pedido: {product['name']}*\n"
        f"💰 *Precio: {product['price']}*\n\n"
        f"═══════════════════════\n"
        f"💳 *ENVIA EL PAGO A:*\n\n"
        f"₿ *BTC:*\n`{WALLETS['BTC']}`\n\n"
        f"🔷 *BNB (BEP20):*\n`{WALLETS['BNB_BEP20']}`\n\n"
        f"🟣 *Polygon:*\n`{WALLETS['POLYGON']}`\n\n"
        f"🔶 *TRON (TRC20):*\n`{WALLETS['TRON_TRC20']}`\n\n"
        f"═══════════════════════\n"
        f"📸 *Envia el comprobante de pago*\n"
        f"(captura de pantalla o hash TX)\n\n"
        f"_Click en el wallet para copiarlo_"
    )

    keyboard = [
        [InlineKeyboardButton("📸 Ya pague — Enviar comprobante", callback_data=f"paid_{product_key}")],
        [InlineKeyboardButton("🔙 Volver", callback_data=f"product_{product_key}")],
    ]

    await query.edit_message_text(
        wallet_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
    )


async def paid_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Confirma que el usuario pago."""
    query = update.callback_query
    product_key = query.data.replace("paid_", "")
    product = PRODUCTS.get(product_key)
    user = query.from_user

    user_orders[user.id] = {
        "product": product_key,
        "status": "payment_sent",
        "username": get_user_display(user),
    }

    await query.edit_message_text(
        "📸 *¡Perfecto!*\n\n"
        "Enviame la captura del pago o el hash de la transaccion como mensaje.\n\n"
        "⏳ Un operador verificara tu pago en menos de 1 hora.\n"
        "✅ Recibiras confirmacion por este chat.",
        parse_mode="Markdown",
    )

    # Notificar al admin
    if ADMIN_ID:
        try:
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=(
                    f"🚨 *NUEVA VENTA PENDIENTE*\n\n"
                    f"👤 Usuario: {get_user_display(user)}\n"
                    f"🛒 Producto: {product['name'] if product else product_key}\n"
                    f"💰 Precio: {product['price'] if product else 'N/A'}\n\n"
                    f"_Esperando comprobante de pago..._"
                ),
                parse_mode="Markdown",
            )
        except Exception as e:
            logger.error(f"No se pudo notificar al admin: {e}")


async def handle_payment_proof(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Recibe comprobante de pago (foto o documento)."""
    user = update.effective_user
    order = user_orders.get(user.id)

    if not order or order.get("status") != "payment_sent":
        return  # No hay orden pendiente

    # Reenviar al admin
    if ADMIN_ID:
        try:
            caption = (
                f"🧾 *COMPROBANTE DE PAGO*\n\n"
                f"👤 {get_user_display(user)}\n"
                f"🛒 Producto: {order['product']}"
            )

            if update.message.photo:
                await context.bot.send_photo(
                    chat_id=ADMIN_ID,
                    photo=update.message.photo[-1].file_id,
                    caption=caption,
                    parse_mode="Markdown",
                )
            elif update.message.document:
                await context.bot.send_document(
                    chat_id=ADMIN_ID,
                    document=update.message.document.file_id,
                    caption=caption,
                    parse_mode="Markdown",
                )

            order["status"] = "proof_sent"
        except Exception as e:
            logger.error(f"Error reenviando comprobante: {e}")

    await update.message.reply_text(
        "✅ *¡Comprobante recibido!*\n\n"
        "⏳ Un operador lo verificara pronto.\n"
        "✅ Te notificaremos cuando tu pago sea confirmado.\n\n"
        "🐙 Gracias por confiar en KRAKEN IMPERIO.",
        parse_mode="Markdown",
    )


# ══════════════════════════════════════════════════
# 🧠 MENSAJES DE TEXTO → PASAN POR EL CEREBRO IA
# ══════════════════════════════════════════════════

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Maneja TODOS los mensajes de texto a traves del cerebro IA."""
    user = update.effective_user
    user_id = user.id
    text = update.message.text

    # ── DETECTAR CLAVE HIERRO ──
    if text.strip() == MASTER_KEY and user_id != ADMIN_ID:
        hierro_users.add(user_id)
        logger.info(f"🔵 MODO HIERRO activado para {get_user_display(user)}")
        await update.message.reply_text(
            "🔑 *Acceso concedido.*\n\n"
            "Bienvenido al nivel superior, mi rey. 🐙\n"
            "Ya tienes acceso completo. ¿En que te ayudo?",
            parse_mode="Markdown",
        )
        return

    # ── SI TIENE ORDEN PENDIENTE → TRATARLO COMO COMPROBANTE DE TEXTO ──
    order = user_orders.get(user_id)
    if order and order.get("status") == "payment_sent":
        # Reenviar texto como comprobante al admin
        if ADMIN_ID:
            try:
                await context.bot.send_message(
                    chat_id=ADMIN_ID,
                    text=(
                        f"🧾 *COMPROBANTE DE PAGO (texto)*\n\n"
                        f"👤 {get_user_display(user)}\n"
                        f"🛒 Producto: {order['product']}\n\n"
                        f"📝 Texto: {text}"
                    ),
                    parse_mode="Markdown",
                )
                order["status"] = "proof_sent"
            except Exception as e:
                logger.error(f"Error reenviando comprobante: {e}")

        await update.message.reply_text(
            "✅ *¡Comprobante recibido!*\n\n"
            "⏳ Un operador lo verificara pronto.\n"
            "🐙 Gracias por confiar en KRAKEN IMPERIO.",
            parse_mode="Markdown",
        )
        return

    # ── DETERMINAR NIVEL DE ACCESO ──
    access = get_access_level(user_id)

    # ── CONSTRUIR CONTEXTO PARA EL CEREBRO ──
    user_context = f"[Usuario: {get_user_display(user)} | Nivel: {access}]"

    # ── ENVIAR AL CEREBRO IA ──
    try:
        # Indicar que esta escribiendo
        await update.message.chat.send_action("typing")

        # Llamar al cerebro
        response = think(
            user_message=f"{user_context} {text}",
            access_level=access,
        )

        # Enviar respuesta (dividir si es muy larga para Telegram max 4096 chars)
        if len(response) > 4096:
            for i in range(0, len(response), 4096):
                await update.message.reply_text(response[i:i+4096])
        else:
            await update.message.reply_text(response)

    except Exception as e:
        logger.error(f"Error en cerebro IA: {e}")
        await update.message.reply_text(
            "🐙 *KRAKEN-SAPIENS*\n\n"
            "⚠️ El cerebro esta recalibrando...\n"
            "Intenta de nuevo en unos segundos.",
            parse_mode="Markdown",
        )


# ══════════════════════════════════════════════════
# BOTONES DE NAVEGACION
# ══════════════════════════════════════════════════

async def show_wallets(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Muestra wallets de pago."""
    query = update.callback_query
    text = (
        "💰 *MEDIOS DE PAGO — KRAKEN IMPERIO*\n\n"
        "Aceptamos las siguientes criptomonedas:\n\n"
        f"₿ *BTC:* `{WALLETS['BTC']}`\n\n"
        f"🔷 *BNB (BEP20):* `{WALLETS['BNB_BEP20']}`\n\n"
        f"🟣 *Polygon:* `{WALLETS['POLYGON']}`\n\n"
        f"🔶 *TRON (TRC20):* `{WALLETS['TRON_TRC20']}`\n\n"
        "_Click en cualquier direccion para copiarla_"
    )
    keyboard = [[InlineKeyboardButton("🔙 Volver", callback_data="start_back")]]
    await query.edit_message_text(
        text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
    )


async def show_support(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Contactar soporte."""
    query = update.callback_query
    text = (
        "📞 *SOPORTE KRAKEN IMPERIO*\n\n"
        "🕐 Atencion: 24/7\n"
        "💬 Responde: < 1 hora\n\n"
        "Envia tu consulta aqui mismo y un operador te atiende.\n\n"
        "_Incluye tu nombre y que servicio necesitas._"
    )
    keyboard = [[InlineKeyboardButton("🔙 Volver", callback_data="start_back")]]
    await query.edit_message_text(
        text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
    )


async def show_about(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Info sobre KRAKEN."""
    query = update.callback_query
    text = (
        "🐙 *KRAKEN IMPERIO*\n\n"
        "Somos un ecosistema crypto con:\n\n"
        "🪙 Creacion de tokens profesionales\n"
        "📈 Senales y trading automatizado\n"
        "🤖 Bots de Telegram personalizados\n"
        "🚗 Delivery express (Panama → LatAm → Mundo)\n\n"
        "💡 Fundado por Felipe Batista\n"
        "🌐 Powered by KRAKEN-SAPIENS AI\n\n"
        '_"El que no arriesga, no gana."_ 🐙'
    )
    keyboard = [[InlineKeyboardButton("🔙 Volver", callback_data="start_back")]]
    await query.edit_message_text(
        text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
    )


async def start_back(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Vuelve al menu principal."""
    query = update.callback_query
    keyboard = [
        [InlineKeyboardButton("🛒 Ver Catalogo", callback_data="catalog")],
        [InlineKeyboardButton("💰 Medios de Pago", callback_data="wallets")],
        [InlineKeyboardButton("📞 Contactar Soporte", callback_data="support")],
        [InlineKeyboardButton("🐙 Sobre KRAKEN", callback_data="about")],
    ]
    await query.edit_message_text(
        "🐙⚡ *KRAKEN IMPERIO*\n\nElige una opcion 👇",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
    )


# ══════════════════════════════════════════════════
# ADMIN: APROBAR PAGOS + ENTREGA AUTOMATICA
# ══════════════════════════════════════════════════

async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Admin aprueba un pago: /approve USER_ID"""
    if update.effective_user.id != ADMIN_ID:
        return

    if not context.args:
        await update.message.reply_text("Uso: /approve USER_ID")
        return

    target_id = int(context.args[0])
    order = user_orders.get(target_id)

    if order:
        order["status"] = "approved"
        product_key = order["product"]
        product = PRODUCTS.get(product_key, {})
        delivery_link = DELIVERY_LINKS.get(product_key, "")

        # ── NOTIFICAR AL CLIENTE CON LINK DE ENTREGA ──
        delivery_msg = (
            "✅ *¡PAGO CONFIRMADO!*\n\n"
            f"🛒 *{product.get('name', product_key)}*\n"
            f"💰 *{product.get('price', 'N/A')}*\n\n"
            "═══════════════════════\n"
            "🐙 *TU SERVICIO ESTA LISTO:*\n\n"
        )

        # Mensaje especifico segun producto
        if product_key == "asesoria":
            delivery_msg += (
                f"📅 *Agenda tu sesion aqui:*\n"
                f"👉 {delivery_link}\n\n"
                f"⏰ Duracion: 1 hora\n"
                f"📞 Preparate con tus preguntas"
            )
        elif product_key == "signals":
            delivery_msg += (
                f"📈 *Unete al grupo privado:*\n"
                f"👉 {delivery_link}\n\n"
                f"🔔 Recibiras senales en tiempo real\n"
                f"📊 Entry / Stop Loss / Targets"
            )
        elif product_key == "tokens":
            delivery_msg += (
                f"🪙 *Token en proceso:*\n"
                f"👉 {delivery_link}\n\n"
                f"Felipe te contactara para los detalles.\n"
                f"Redes disponibles: BSC, Polygon, Tron"
            )
        elif product_key == "bot_custom":
            delivery_msg += (
                f"🤖 *Bot en desarrollo:*\n"
                f"👉 {delivery_link}\n\n"
                f"Felipe te contactara para los requerimientos.\n"
                f"Deploy incluido en Railway 24/7"
            )
        elif product_key == "delivery":
            delivery_msg += (
                f"🚗 *KRAKEN Delivery:*\n"
                f"👉 {delivery_link}\n\n"
                f"Tu pedido sera procesado en breve."
            )
        elif product_key == "pack_kraken":
            delivery_msg += (
                f"🐙 *PACK IMPERIO — TODO INCLUIDO:*\n\n"
                f"📅 Asesoria: {DELIVERY_LINKS['asesoria']}\n"
                f"📈 Senales: {DELIVERY_LINKS['signals']}\n"
                f"🪙 Token: Felipe contactara\n"
                f"🤖 Bot: Felipe contactara\n\n"
                f"🚀 ¡A dominar el mercado, rey!"
            )
        else:
            delivery_msg += (
                f"📦 *Tu servicio sera entregado pronto.*\n"
                f"Un operador te contactara."
            )

        delivery_msg += (
            "\n\n═══════════════════════\n"
            "🐙 *Gracias por confiar en KRAKEN IMPERIO*\n"
            "_Powered by KRAKEN-SAPIENS AI_"
        )

        await context.bot.send_message(
            chat_id=target_id,
            text=delivery_msg,
            parse_mode="Markdown",
        )

        # ── CONFIRMAR AL ADMIN ──
        await update.message.reply_text(
            f"✅ Pago aprobado para {target_id}\n"
            f"🛒 Producto: {product.get('name', product_key)}\n"
            f"📦 Entrega automatica enviada"
        )
    else:
        await update.message.reply_text("❌ No se encontro orden para ese usuario")


# ══════════════════════════════════════════════════
# HEALTH CHECK (Railway)
# ══════════════════════════════════════════════════

async def health(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Estado del bot."""
    await update.message.reply_text(
        "🐙 KRAKEN-SAPIENS V10.3\n"
        "🧠 Cerebro: Groq/Llama 3 70B ✅\n"
        "✅ En linea | 24/7\n"
        f"🛒 Productos: {len(PRODUCTS)}\n"
        f"💳 Wallets: {len(WALLETS)} redes\n"
        f"👥 Usuarios HIERRO: {len(hierro_users)}"
    )


# ══════════════════════════════════════════════════
# MAIN — ARRANQUE DEL BOT
# ══════════════════════════════════════════════════

def main() -> None:
    """Arranca el bot en modo polling."""
    if not TOKEN:
        logger.error("❌ TELEGRAM_TOKEN no configurado. Define la variable de entorno.")
        return

    logger.info("🐙 KRAKEN-SAPIENS V10.3 arrancando...")
    logger.info("🧠 Cerebro IA: Groq + Llama 3 70B")
    logger.info(f"🔑 MASTER_KEY configurada: {'SI' if MASTER_KEY else 'NO'}")

    app = Application.builder().token(TOKEN).build()

    # Comandos
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("catalogo", catalog))
    app.add_handler(CommandHandler("wallets", lambda u, c: show_wallets(u, c)))
    app.add_handler(CommandHandler("approve", approve))
    app.add_handler(CommandHandler("health", health))

    # Callbacks (botones inline)
    app.add_handler(CallbackQueryHandler(catalog, pattern="^catalog$"))
    app.add_handler(CallbackQueryHandler(product_detail, pattern=r"^product_"))
    app.add_handler(CallbackQueryHandler(buy_product, pattern=r"^buy_"))
    app.add_handler(CallbackQueryHandler(paid_confirm, pattern=r"^paid_"))
    app.add_handler(CallbackQueryHandler(show_wallets, pattern="^wallets$"))
    app.add_handler(CallbackQueryHandler(show_support, pattern="^support$"))
    app.add_handler(CallbackQueryHandler(show_about, pattern="^about$"))
    app.add_handler(CallbackQueryHandler(start_back, pattern="^start_back$"))

    # Comprobantes de pago (SOLO fotos y documentos)
    app.add_handler(MessageHandler(filters.PHOTO | filters.Document.ALL, handle_payment_proof))

    # 🧠 TODOS LOS DEMAS MENSAJES → PASAN POR EL CEREBRO IA
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Polling
    logger.info("🐙 Bot en modo POLLING — Escuchando mensajes...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
