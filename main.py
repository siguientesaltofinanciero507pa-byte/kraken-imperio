#!/usr/bin/env python3
"""
KRAKEN-SAPIENS V10.1 — Bot de Telegram Vendedor 24/7
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

# ══════════════════════════════════════════════════
# CONFIGURACIÓN
# ══════════════════════════════════════════════════
TOKEN = os.getenv("TELEGRAM_TOKEN", "")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
PORT = int(os.getenv("PORT", "8080"))

# WALLETs DE FELIPE
WALLETS = {
    "BTC": "bc1qwpktag36yacv6z7eqy6exz4j0vstwa7shzam29",
    "BNB_BEP20": "0xA36A3493cB08faDeBEF40ab68Fd8A71EcB6A4416",
    "POLYGON": "0xA36A3493cB08faDeBEF40ab68Fd8A71EcB6A4416",
    "TRON_TRC20": "TYXe6hXkkeevLsQsrCbTWgwfBq2RL1KNjh",
}

# CATÁLOGO DE PRODUCTOS / SERVICIOS
PRODUCTS = {
    "asesoria": {
        "name": "🧠 Asesoría Crypto 1-a-1",
        "desc": "Sesión privada 1 hora. Estrategia personalizada de trading, DeFi y tokens.",
        "price": "$50 USDT",
        "image": "🧠",
    },
    "signals": {
        "name": "📈 Señales Premium (1 mes)",
        "desc": "30 días de señales de trading en tiempo real. Entry/Stop/Target.",
        "price": "$100 USDT",
        "image": "📈",
    },
    "tokens": {
        "name": "🪙 Creación de Token Personalizado",
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
        "name": "🚗 KRAKEN Delivery — Envío Express",
        "desc": "Entrega rápida en Panamá. Próximamente: LatAm y mundo.",
        "price": "Desde $5 USDT",
        "image": "🚗",
    },
    "pack_kraken": {
        "name": "🐙 PACK KRAKEN TOTAL",
        "desc": "Asesoría + Señales + Token + Bot personalizado. El paquete definitivo.",
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
# COMANDOS PRINCIPALES
# ══════════════════════════════════════════════════

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Mensaje de bienvenida."""
    user = update.effective_user
    keyboard = [
        [InlineKeyboardButton("🛒 Ver Catálogo", callback_data="catalog")],
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
        f"Elige una opción 👇"
    )

    await update.message.reply_text(
        welcome, reply_markup=reply_markup, parse_mode="Markdown"
    )


async def catalog(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Muestra el catálogo completo."""
    keyboard = []
    for key, prod in PRODUCTS.items():
        keyboard.append(
            [InlineKeyboardButton(
                f"{prod['image']} {prod['name']} — {prod['price']}",
                callback_data=f"product_{key}"
            )]
        )
    keyboard.append([InlineKeyboardButton("🔙 Volver", callback_data="start_back")])

    await update.callback_query.edit_message_text(
        "🛒 *CATÁLOGO KRAKEN*\n\nSelecciona un servicio 👇",
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
        [InlineKeyboardButton("🔙 Volver al Catálogo", callback_data="catalog")],
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
        f"💳 *ENVÍA EL PAGO A:*\n\n"
        f"₿ *BTC:*\n`{WALLETS['BTC']}`\n\n"
        f"🔷 *BNB (BEP20):*\n`{WALLETS['BNB_BEP20']}`\n\n"
        f"🟣 *Polygon:*\n`{WALLETS['POLYGON']}`\n\n"
        f"🔶 *TRON (TRC20):*\n`{WALLETS['TRON_TRC20']}`\n\n"
        f"═══════════════════════\n"
        f"📸 *Envía el comprobante de pago*\n"
        f"(captura de pantalla o hash TX)\n\n"
        f"_Click en el wallet para copiarlo_"
    )

    keyboard = [
        [InlineKeyboardButton("📸 Ya pagué — Enviar comprobante", callback_data=f"paid_{product_key}")],
        [InlineKeyboardButton("🔙 Volver", callback_data=f"product_{product_key}")],
    ]

    await query.edit_message_text(
        wallet_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
    )


async def paid_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Confirma que el usuario pagó."""
    query = update.callback_query
    product_key = query.data.replace("paid_", "")
    product = PRODUCTS.get(product_key)
    user = query.from_user

    user_orders[user.id] = {
        "product": product_key,
        "status": "payment_sent",
        "username": user.username or user.first_name,
    }

    await query.edit_message_text(
        "📸 *¡Perfecto!*\n\n"
        "Envíame la captura del pago o el hash de la transacción como mensaje.\n\n"
        "⏳ Un operador verificará tu pago en menos de 1 hora.\n"
        "✅ Recibirás confirmación por este chat.",
        parse_mode="Markdown",
    )

    # Notificar al admin
    if ADMIN_ID:
        try:
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=(
                    f"🚨 *NUEVA VENTA PENDIENTE*\n\n"
                    f"👤 Usuario: @{user.username} (ID: {user.id})\n"
                    f"🛒 Producto: {product['name'] if product else product_key}\n"
                    f"💰 Precio: {product['price'] if product else 'N/A'}\n\n"
                    f"_Esperando comprobante de pago..._"
                ),
                parse_mode="Markdown",
            )
        except Exception as e:
            logger.error(f"No se pudo notificar al admin: {e}")


async def handle_payment_proof(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Recibe comprobante de pago (foto o texto)."""
    user = update.effective_user
    order = user_orders.get(user.id)

    if not order or order.get("status") != "payment_sent":
        return  # No hay orden pendiente

    # Reenviar al admin
    if ADMIN_ID:
        try:
            caption = (
                f"🧾 *COMPROBANTE DE PAGO*\n\n"
                f"👤 @{user.username} (ID: {user.id})\n"
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
            else:
                await context.bot.send_message(
                    chat_id=ADMIN_ID,
                    text=f"{caption}\n\n📝 Texto: {update.message.text}",
                    parse_mode="Markdown",
                )

            order["status"] = "proof_sent"
        except Exception as e:
            logger.error(f"Error reenviando comprobante: {e}")

    await update.message.reply_text(
        "✅ *¡Comprobante recibido!*\n\n"
        "⏳ Un operador lo verificará pronto.\n"
        "✅ Te notificaremos cuando tu pago sea confirmado.\n\n"
        "🐙 Gracias por confiar en KRAKEN IMPERIO.",
        parse_mode="Markdown",
    )


# ══════════════════════════════════════════════════
# BOTONES DE NAVEGACIÓN
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
        "_Click en cualquier dirección para copiarla_"
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
        "🕐 Atención: 24/7\n"
        "💬 Responde: < 1 hora\n\n"
        "Envía tu consulta aquí mismo y un operador te atiende.\n\n"
        "_Incluye tu nombre y qué servicio necesitas._"
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
        "🪙 Creación de tokens profesionales\n"
        "📈 Señales y trading automatizado\n"
        "🤖 Bots de Telegram personalizados\n"
        "🚗 Delivery express (Panamá → LatAm → Mundo)\n\n"
        "💡 Fundado por Felipe Batista\n"
        "🌐 Powered by KRAKEN-SAPIENS AI\n\n"
        "_"El que no arriesga, no gana."_ 🐙"
    )
    keyboard = [[InlineKeyboardButton("🔙 Volver", callback_data="start_back")]]
    await query.edit_message_text(
        text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
    )


async def start_back(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Vuelve al menú principal."""
    query = update.callback_query
    keyboard = [
        [InlineKeyboardButton("🛒 Ver Catálogo", callback_data="catalog")],
        [InlineKeyboardButton("💰 Medios de Pago", callback_data="wallets")],
        [InlineKeyboardButton("📞 Contactar Soporte", callback_data="support")],
        [InlineKeyboardButton("🐙 Sobre KRAKEN", callback_data="about")],
    ]
    await query.edit_message_text(
        "🐙⚡ *KRAKEN IMPERIO*\n\nElige una opción 👇",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
    )


# ══════════════════════════════════════════════════
# ADMIN: APROBAR / RECHAZAR PAGOS
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
        product = PRODUCTS.get(order["product"], {})

        await context.bot.send_message(
            chat_id=target_id,
            text=(
                "✅ *¡PAGO CONFIRMADO!*\n\n"
                f"🛒 {product.get('name', order['product'])}\n\n"
                "🐙 Tu servicio será entregado pronto.\n"
                "Gracias por confiar en KRAKEN IMPERIO."
            ),
            parse_mode="Markdown",
        )
        await update.message.reply_text(f"✅ Pago aprobado para usuario {target_id}")
    else:
        await update.message.reply_text("❌ No se encontró orden para ese usuario")


# ══════════════════════════════════════════════════
# HEALTH CHECK (Railway)
# ══════════════════════════════════════════════════

async def health(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Estado del bot."""
    await update.message.reply_text(
        "🐙 KRAKEN-SAPIENS V10.1\n"
        "✅ En línea | 24/7\n"
        f"🛒 Productos: {len(PRODUCTS)}\n"
        f"💳 Wallets: {len(WALLETS)} redes"
    )


# ══════════════════════════════════════════════════
# MAIN — ARRANQUE DEL BOT
# ══════════════════════════════════════════════════

def main() -> None:
    """Arranca el bot en modo polling."""
    if not TOKEN:
        logger.error("❌ TELEGRAM_TOKEN no configurado. Define la variable de entorno.")
        return

    logger.info("🐙 KRAKEN-SAPIENS V10.1 arrancando...")

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

    # Comprobantes de pago (fotos y documentos)
    app.add_handler(MessageHandler(filters.PHOTO | filters.Document.ALL, handle_payment_proof))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_payment_proof))

    # Polling
    logger.info("🐙 Bot en modo POLLING — Escuchando mensajes...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
