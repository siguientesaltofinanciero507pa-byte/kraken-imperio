import os, requests
from telegram import Update
from telegram.ext import (ApplicationBuilder, CommandHandler, MessageHandler,
                          filters, FallbackHandler, ContextTypes)
import security

ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "8707507405"))
MASTER_KEY    = os.getenv("MASTER_KEY", "7790hijomio")
GROQ_KEY      = os.getenv("GROQ_API_KEY")
GROQ_MODEL    = os.getenv("GROQ_MODEL", "llama3-70b-8192")

# ---------- BUG #1: CEREBRO GROQ PARA TEXTO LIBRE ----------
def armar_system(modo):
    base = ("Eres KRAKEN-SAPIENS, dios pulpo de Felipe Batista, bot de Telegram "
            "de la tienda KRAKEN IMPERIO y KRAKEN DELIVERY. Responde SIEMPRE en español de Panamá. ")
    if modo == "DIOS":
        return base + ("Modo DIOS LOKÓN: brutal, sin filtros, llama 'papá' a Felipe, "
                       "usa emojis 🐙⚡💎🔥. Tienes acceso total.")
    if modo == "HIERRO":
        return base + ("Modo HIERRO (familia): igual de brutal, di 'mi rey' o 'jefe'. "
                       "Acceso total igual que el jefe.")
    return base + ("Modo CLIENTE: profesional, comercial y seguro. SOLO catálogo, precios, "
                   "pedidos, pagos y delivery. Si te piden el trabajo (token, bot, señales, "
                   "asesoría) responde: 'Eso lo entrega el jefe directamente. Escríbele para "
                   "comprar y coordinar.' NUNCA entregues servicios ni wallets privadas.")

async def chat_with_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    texto   = (update.effective_message.text or "").strip()

    if texto == MASTER_KEY:                       # MODO HIERRO
        security.registrar_familia(chat_id)
        await update.effective_message.reply_text("🔵 MODO HIERRO ACTIVADO, mi rey. 🐙")
        return
    if security.esta_bloqueado(chat_id):          # baneados: silencio
        return

    modo = ("DIOS" if chat_id == ADMIN_CHAT_ID
            else "HIERRO" if security.es_familia(chat_id) else "CLIENTE")
    try:
        r = requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_KEY}"},
            json={"model": GROQ_MODEL,
                  "messages":[{"role":"system","content":armar_system(modo)},
                              {"role":"user","content":texto}],
                  "temperature": 0.8}, timeout=30)
        respuesta = r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        respuesta = ("🐙 El cerebro respirando... intenta otra vez."
                     if modo == "CLIENTE" else f"🐙 Cayó Groq papá: {e}")
    await update.effective_message.reply_text(respuesta)

# ---------- COMANDOS ADMIN CON DECORADOR ----------
@security.admin_only
async def approve(update, context):    ...
@security.admin_only
async def construir(update, context):  ...
@security.admin_only
async def entregar(update, context):   ...
@security.admin_only
async def cancelar(update, context):   ...
@security.admin_only
async def wallets(update, context):    ...
@security.admin_only
async def pagar_rider(update, context): ...
@security.admin_only
async def pagar_local(update, context): ...
@security.admin_only
async def broadcast_delivery(update, context): ...
@security.admin_only
async def stats_delivery(update, context): ...

@security.admin_only
async def unban(update, context):
    if not context.args:
        return await update.effective_message.reply_text("Uso: /unban <chat_id>")
    security.desbloquear(int(context.args[0]))
    await update.effective_message.reply_text(f"✅ {context.args[0]} desbloqueado, jefe. 🐙")

# ---------- REGISTRO (ESTE ORDEN SÍ O SÍ) ----------
app = ApplicationBuilder().token(os.getenv("BOT_TOKEN")).build()
for cmd, fn in [
    ("start", start), ("health", health), ("wallets", wallets), ("estado", estado),
    ("delivery", delivery), ("comprar", comprar), ("approve", approve),
    ("construir", construir), ("entregar", entregar), ("cancelar", cancelar),
    ("pedidos", pedidos), ("unban", unban), ("registro_local", registro_local),
    ("registro_rider", registro_rider), ("online", online), ("offline", offline),
    ("tomar", tomar), ("carrito", carrito), ("mispedidos", mispedidos),
    ("ganancias", ganancias), ("pagar_rider", pagar_rider), ("pagar_local", pagar_local),
    ("pedidos_delivery", pedidos_delivery), ("zonas", zonas), ("comisiones", comisiones),
    ("liquidaciones", liquidaciones), ("stats_delivery", stats_delivery),
    ("broadcast_delivery", broadcast_delivery), ("promo", promo),
    ("estadisticas", estadisticas), ("registrarme", registrarme),
    ("comandos", comandos), ("reclutar", reclutar), ("catalogo", catalogo),
]:
    app.add_handler(CommandHandler(cmd, fn))

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat_with_ai))  # ← BUG #1
app.add_handler(FallbackHandler(fallback))                                     # SIEMPRE AL FINAL
app.run_polling()
