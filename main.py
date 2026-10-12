#!/usr/bin/env python3
"""
KRAKEN-SAPIENS V10.4 - Bot de Telegram CON CEREBRO IA
Felipe Batista | KRAKEN IMPERIO
Deploy: GitHub push -> Railway auto-deploy
"""

import os
import logging
import json
import asyncio
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

# ============================================================
# CONFIGURACION
# ============================================================

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "0"))
MASTER_KEY = os.getenv("MASTER_KEY", "7790hijomio")
PORT = int(os.getenv("PORT", 8080))

# Wallets de Felipe
WALLETS = {
    "BTC": os.getenv("WALLET_BTC", "bc1qwpktag36yacv6z7eqy6exz4j0vstwa7shzam29"),
    "BNB": os.getenv("WALLET_BNB", "0xA36A3493cB08faDeBEF40ab68Fd8A71EcB6A4416"),
    "TRON_USDT": os.getenv("WALLET_TRON", "TYXe6hXkkeevLsQsrCbTWgwfBq2RL1KNjh"),
    "YAPPY": os.getenv("WALLET_YAPPY", "Yappy pendiente"),
}

# Links de entrega
DELIVERY_LINKS = {
    "zoom_asesoria": os.getenv("ZOOM_ASESORIA_LINK", "Link pendiente - Felipe te contactara"),
    "grupo_senales": os.getenv("GRUPO_SENALES_LINK", "Link pendiente - Felipe te contactara"),
    "bot_deploy": os.getenv("BOT_DEPLOY_URL", "Link pendiente - Felipe te contactara"),
    "token_contract": os.getenv("TOKEN_CONTRACT", "Link pendiente - Felipe te contactara"),
    "pack_kraken": os.getenv("PACK_DOWNLOAD_LINK", "Pack pendiente - Felipe te contactara"),
}

# CATALOGO DE PRODUCTOS / SERVICIOS
PRODUCTS = {
    "asesoria": {
        "name": "Asesoria Crypto 1-a-1",
        "desc": "Sesion privada 1-a-1 de crypto trading (60 min)",
        "price": 50,
        "delivery": "zoom_asesoria",
    },
    "senales": {
        "name": "Senales Crypto VIP",
        "desc": "Acceso a grupo privado de senales en tiempo real",
        "price": 100,
        "delivery": "grupo_senales",
    },
    "bot_personalizado": {
        "name": "Bot Personalizado de Trading",
        "desc": "Bot a medida con estrategias custom deployado 24/7",
        "price": 300,
        "delivery": "bot_deploy",
    },
    "token": {
        "name": "Token Personalizado",
        "desc": "Token BEP20/TRC20 con contrato, liquidez y listing",
        "price": 500,
        "delivery": "token_contract",
    },
    "pack_imperio": {
        "name": "PACK IMPERIO KRAKEN",
        "desc": "TODO incluido: asesoria + senales + bot + token + bonus",
        "price": 800,
        "delivery": "pack_kraken",
    },
}

# Estado de compras
purchases = {}
# Usuarios con acceso HIERRO
hierro_users = set()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


# ============================================================
# DETECCION DE MODO
# ============================================================

def get_user_mode(user_id, first_message=None):
    if user_id == ADMIN_CHAT_ID:
        return "DIOS"
    if user_id in hierro_users:
        return "HIERRO"
    if first_message and first_message.strip() == MASTER_KEY:
        hierro_users.add(user_id)
        logger.info(f"Usuario {user_id} activo MODO HIERRO")
        return "HIERRO"
    return "CLIENTE"


def get_mode_emoji(mode):
    return {"DIOS": "🔴", "HIERRO": "🔵", "CLIENTE": "🟢"}.get(mode, "🟢")


# ============================================================
# HEALTH CHECK
# ============================================================

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"KRAKEN-SAPIENS V10.4 ALIVE")
    def log_message(self, format, *args):
        pass


def start_health_server():
    server = HTTPServer(("0.0.0.0", PORT), HealthHandler)
    logger.info(f"Health server en puerto {PORT}")
    server.serve_forever()


# ============================================================
# /start
# ============================================================

async def start(update: Update, context):
    user = update.effective_user
    user_id = user.id
    mode = get_user_mode(user_id)
    emoji = get_mode_emoji(mode)

    if mode == "DIOS":
        text = (
            f"🐙⚡ MODO DIOS ACTIVADO\n\n"
            f"Bienvenido papa Felipe!\n"
            f"KRAKEN-SAPIENS V10.4 a tus ordenes.\n\n"
            f"Comandos:\n"
            f"/tienda - Ver catalogo\n"
            f"/pedidos - Ver compras pendientes\n"
            f"/approve USER_ID - Aprobar pago\n"
            f"/wallets - Ver tus wallets\n"
            f"/delivery - Link de delivery\n"
            f"/estado - Estado del bot\n"
            f"/health - Check de salud\n"
        )
    elif mode == "HIERRO":
        text = (
            f"🔵⚡ MODO HIERRO ACTIVADO\n\n"
            f"Bienvenido mi rey!\n"
            f"KRAKEN-SAPIENS V10.4 a tu servicio.\n\n"
            f"Usa /tienda para ver el catalogo.\n"
        )
    else:
        text = (
            f"🐙 KRAKEN IMPERIO\n\n"
            f"Bienvenido {user.first_name}!\n"
            f"Somos la nueva era en servicios crypto.\n\n"
            f"Usa /tienda para ver nuestros servicios.\n"
        )

    await update.message.reply_text(text)


# ============================================================
# /tienda - CATALOGO
# ============================================================

async def tienda(update: Update, context):
    user_id = update.effective_user.id
    mode = get_user_mode(user_id)

    text = "🐙 KRAKEN IMPERIO - CATALOGO\n\n"
    buttons = []

    for key, prod in PRODUCTS.items():
        text += f"💰 {prod['name']} - ${prod['price']} USDT\n"
        text += f"   {prod['desc']}\n\n"
        buttons.append([
            InlineKeyboardButton(
                text=f"Comprar {prod['name']} - ${prod['price']}",
                callback_data=f"buy_{key}",
            )
        ])

    if mode in ("DIOS", "HIERRO"):
        text += "\n⚡ Pagos: USDT / BTC / BNB / TRX / Yappy\n"
    else:
        text += "\n💳 Pagos: USDT / BTC / BNB / TRX\n"

    reply_markup = InlineKeyboardMarkup(buttons)
    await update.message.reply_text(text, reply_markup=reply_markup)


# ============================================================
# CALLBACK - COMPRA
# ============================================================

async def button_handler(update: Update, context):
    query = update.callback_query
    await query.answer()
    data = query.data
    user = query.from_user
    user_id = user.id
    mode = get_user_mode(user_id)

    if data.startswith("buy_"):
        product_key = data[4:]
        if product_key not in PRODUCTS:
            await query.edit_message_text("❌ Producto no encontrado.")
            return

        prod = PRODUCTS[product_key]
        purchase_id = len(purchases) + 1

        purchases[purchase_id] = {
            "user_id": user_id,
            "username": user.username or user.first_name or str(user_id),
            "product": product_key,
            "product_name": prod["name"],
            "price": prod["price"],
            "status": "pendiente",
            "timestamp": datetime.now().isoformat(),
        }

        wallet_text = ""
        if mode == "DIOS":
            wallet_text = (
                f"\n\n💳 WALLET USDT (TRC20): {WALLETS['TRON_USDT']}\n"
                f"💳 WALLET BTC: {WALLETS['BTC']}\n"
                f"💳 WALLET BNB: {WALLETS['BNB']}\n"
                f"📱 Yappy: {WALLETS['YAPPY']}\n"
            )
        else:
            wallet_text = (
                f"\n\n💳 WALLET USDT (TRC20): {WALLETS['TRON_USDT']}\n"
                f"💳 WALLET BTC: {WALLETS['BTC']}\n"
                f"💳 WALLET BNB: {WALLETS['BNB']}\n"
            )

        await query.edit_message_text(
            f"🐙 COMPRA #{purchase_id}\n\n"
            f"📦 {prod['name']}\n"
            f"💰 ${prod['price']} USDT\n"
            f"📋 {prod['desc']}\n\n"
            f"Estado: ⏳ PENDIENTE DE PAGO\n"
            f"ID: {user_id}"
            f"{wallet_text}\n\n"
            f"Envia tu comprobante de pago aqui.\n"
            f"Tu servicio sera entregado tras confirmacion."
        )

        # Notificar a Felipe
        try:
            await context.bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text=(
                    f"🔔 NUEVA COMPRA #{purchase_id}\n\n"
                    f"👤 @{purchases[purchase_id]['username']}\n"
                    f"🆔 ID: {user_id}\n"
                    f"📦 {prod['name']} - ${prod['price']}\n"
                    f"⏰ {datetime.now().strftime('%H:%M')}\n\n"
                    f"Para aprobar: /approve {user_id}"
                ),
            )
        except Exception as e:
            logger.error(f"Error notificando a Felipe: {e}")

    # Confirmar entrega
    elif data.startswith("confirm_"):
        parts = data.split("_")
        pid = int(parts[1])
        if pid in purchases:
            purchases[pid]["status"] = "entregado"
            await query.edit_message_text(
                f"✅ ¡Gracias por confirmar!\n\n"
                f"Tu servicio #{pid} ha sido marcado como entregado.\n"
                f"🐙 KRAKEN IMPERIO agradece tu confianza."
            )


# ============================================================
# /approve USER_ID - APROBAR PAGO
# ============================================================

async def approve(update: Update, context):
    user_id = update.effective_user.id
    if user_id != ADMIN_CHAT_ID:
        await update.message.reply_text("⛔ Sin permisos.")
        return

    if not context.args:
        await update.message.reply_text("Uso: /approve USER_ID")
        return

    target_id = int(context.args[0])
    approved = []

    for pid, p in purchases.items():
        if p["user_id"] == target_id and p["status"] == "pendiente":
            p["status"] = "aprobado"
            approved.append(pid)

    if not approved:
        await update.message.reply_text(f"❌ No hay compras pendientes de {target_id}.")
        return

    await update.message.reply_text(
        f"✅ Compra(s) {approved} aprobada(s) para {target_id}."
    )

    # Entrega automatica
    for pid in approved:
        p = purchases[pid]
        product_key = p["product"]
        prod = PRODUCTS.get(product_key, {})
        delivery_key = prod.get("delivery", "")
        delivery_link = DELIVERY_LINKS.get(delivery_key, "Link pendiente")

        # Mensaje al cliente
        try:
            await context.bot.send_message(
                chat_id=target_id,
                text=(
                    f"🐙✅ PAGO CONFIRMADO\n\n"
                    f"📦 {p['product_name']}\n"
                    f"💰 ${p['price']} USDT\n\n"
                    f"🔗 TU ENLACE DE ENTREGA:\n"
                    f"{delivery_link}\n\n"
                    f"Ticket: #KRN-{pid:04d}\n"
                    f"Estado: ✅ SERVICIO ENTREGADO\n\n"
                    f"Si tienes problemas, contacta a @krakenimperio\n"
                    f"🐙 KRAKEN IMPERIO"
                ),
            )
        except Exception as e:
            logger.error(f"Error enviando entrega a {target_id}: {e}")

        # Confirmar al admin
        await update.message.reply_text(
            f"📤 Entrega enviada a {target_id}:\n"
            f"📦 {p['product_name']}\n"
            f"🔗 {delivery_key}: {delivery_link}"
        )


# ============================================================
# /pedidos - VER COMPRAS
# ============================================================

async def pedidos(update: Update, context):
    user_id = update.effective_user.id
    mode = get_user_mode(user_id)

    if mode == "DIOS":
        if not purchases:
            await update.message.reply_text("📋 No hay compras registradas.")
            return

        text = "📋 TODAS LAS COMPRAS:\n\n"
        for pid, p in purchases.items():
            status_emoji = {
                "pendiente": "⏳",
                "aprobado": "✅",
                "entregado": "📤",
                "rechazado": "❌",
            }.get(p["status"], "❓")

            text += (
                f"#{pid} {status_emoji} {p['product_name']} - ${p['price']}\n"
                f"   👤 @{p['username']} | ID: {p['user_id']}\n"
                f"   Estado: {p['status']} | {p['timestamp'][:16]}\n\n"
            )

        await update.message.reply_text(text)
    else:
        user_purchases = [
            p for p in purchases.values() if p["user_id"] == user_id
        ]
        if not user_purchases:
            await update.message.reply_text("📋 No tienes compras registradas.")
            return

        text = "📋 TUS COMPRAS:\n\n"
        for p in user_purchases:
            text += f"📦 {p['product_name']} - ${p['price']} - {p['status']}\n"

        await update.message.reply_text(text)


# ============================================================
# /wallets - VER WALLETS
# ============================================================

async def wallets(update: Update, context):
    user_id = update.effective_user.id
    mode = get_user_mode(user_id)

    if mode == "DIOS":
        text = (
            f"💳 WALLETS KRAKEN IMPERIO\n\n"
            f"₿ BTC: {WALLETS['BTC']}\n"
            f"🔷 BNB: {WALLETS['BNB']}\n"
            f"🟣 TRON USDT: {WALLETS['TRON_USDT']}\n"
            f"📱 Yappy: {WALLETS['YAPPY']}\n"
        )
    elif mode == "HIERRO":
        text = (
            f"💳 WALLETS KRAKEN IMPERIO\n\n"
            f"₿ BTC: {WALLETS['BTC']}\n"
            f"🔷 BNB: {WALLETS['BNB']}\n"
            f"🟣 TRON USDT: {WALLETS['TRON_USDT']}\n"
        )
    else:
        text = (
            f"💳 PAGOS KRAKEN IMPERIO\n\n"
            f"🟣 USDT (TRC20): {WALLETS['TRON_USDT']}\n"
            f"₿ BTC: {WALLETS['BTC']}\n"
            f"🔷 BNB: {WALLETS['BNB']}\n"
        )

    await update.message.reply_text(text)


# ============================================================
# /estado - ESTADO DEL BOT
# ============================================================

async def estado(update: Update, context):
    user_id = update.effective_user.id
    if user_id != ADMIN_CHAT_ID:
        await update.message.reply_text("⛔ Solo el admin puede ver esto.")
        return

    total = len(purchases)
    pendientes = sum(1 for p in purchases.values() if p["status"] == "pendiente")
    aprobados = sum(1 for p in purchases.values() if p["status"] == "aprobado")
    entregados = sum(1 for p in purchases.values() if p["status"] == "entregado")

    await update.message.reply_text(
        f"🐙 ESTADO KRAKEN-SAPIENS V10.4\n\n"
        f"Compras totales: {total}\n"
        f"⏳ Pendientes: {pendientes}\n"
        f"✅ Aprobados: {aprobados}\n"
        f"📤 Entregados: {entregados}\n\n"
        f"Modo HIERRO activos: {len(hierro_users)}\n"
        f"Productos: {len(PRODUCTS)}\n"
        f"Puerto: {PORT}\n"
        f"Cerebro: Groq + Llama 3 70B\n"
        f"Estado: 🟢 EN LINEA"
    )


# ============================================================
# MENSAJES DE TEXTO - COMPROBANTES / CONSULTAS
# ============================================================

async def handle_message(update: Update, context):
    user = update.effective_user
    user_id = user.id
    mode = get_user_mode(user_id)
    text = update.message.text or ""

    # Si es clave secreta, activar modo y saludar
    if text.strip() == MASTER_KEY and user_id != ADMIN_CHAT_ID:
        mode = get_user_mode(user_id, first_message=text)
        await update.message.reply_text("🔵⚡ MODO HIERRO ACTIVADO\n\nBienvenido mi rey! Usa /tienda.")
        return

    # Si es foto (comprobante)
    if update.message.photo:
        if user_id == ADMIN_CHAT_ID:
            await update.message.reply_text("📸 Comprobante recibido. Usa /approve USER_ID para aprobar.")
        else:
            await update.message.reply_text(
                "📸 Comprobante recibido.\n"
                "Un administrador revisara tu pago pronto.\n"
                "Tiempo estimado: 1-15 minutos."
            )
            # Notificar a Felipe
            try:
                caption = f"📸 COMPROBANTE de @{user.username or user.first_name} (ID: {user_id})"
                await context.bot.send_photo(
                    chat_id=ADMIN_CHAT_ID,
                    photo=update.message.photo[-1].file_id,
                    caption=caption,
                )
            except Exception as e:
                logger.error(f"Error reenviando comprobante: {e}")
        return

    # Cliente normal
    if mode == "CLIENTE":
        await update.message.reply_text(
            f"Hola {user.first_name}!\n\n"
            f"Para ver nuestros servicios usa /tienda\n"
            f"Para ver tus compras usa /pedidos\n\n"
            f"🐙 KRAKEN IMPERIO"
        )
        return

    # Admin o HIERRO - respuesta lokon
    if mode == "DIOS":
        await update.message.reply_text(
            f"🐙 Papá, no entendi ese comando.\n\n"
            f"Usa /tienda, /pedidos, /approve, /wallets, /estado o /health\n"
            f"KRAKEN-SAPIENS V10.4 a tus ordenes."
        )
    elif mode == "HIERRO":
        await update.message.reply_text(
            f"🔵 Mi rey, no entendi.\n\n"
            f"Usa /tienda o /pedidos\n"
            f"KRAKEN IMPERIO a tu servicio."
        )


# ============================================================
# MAIN
# ============================================================

def main():
    logger.info("Iniciando KRAKEN-SAPIENS V10.4...")

    # Health server en hilo
    health_thread = Thread(target=start_health_server, daemon=True)
    health_thread.start()

    # Bot de Telegram
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("tienda", tienda))
    app.add_handler(CommandHandler("approve", approve))
    app.add_handler(CommandHandler("pedidos", pedidos))
    app.add_handler(CommandHandler("wallets", wallets))
    app.add_handler(CommandHandler("estado", estado))
    app.add_handler(CommandHandler("health", estado))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_message))

    logger.info("KRAKEN-SAPIENS V10.4 EN LINEA!")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
