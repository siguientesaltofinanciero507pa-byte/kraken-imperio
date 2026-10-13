# ============================================================
# security.py — KRAKEN V10.6 · DEFENSA ANTI-TROL (B + C)
# ============================================================
import json, os, time
from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes

MASTER_KEY      = os.getenv("MASTER_KEY", "7790hijomio")
ADMIN_CHAT_ID   = int(os.getenv("ADMIN_CHAT_ID", "8707507405"))
EMPIRE_GROUP_ID = int(os.getenv("EMPIRE_GROUP_ID", str(ADMIN_CHAT_ID)))
DIAS = 30 * 86400  # el contador se resetea cada 30 días

def _load(nombre):
    try:
        with open(nombre, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def _save(nombre, data):
    with open(nombre, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ---------- FAMILIA (MODO HIERRO) ----------
def registrar_familia(chat_id):
    fam = _load("familia.json"); fam[str(chat_id)] = {"desde": time.time()}
    _save("familia.json", fam)

def es_familia(chat_id):
    return str(chat_id) in _load("familia.json")

def es_admin(chat_id):
    return chat_id == ADMIN_CHAT_ID or es_familia(chat_id)

# ---------- BLOQUEADOS ----------
def esta_bloqueado(chat_id):
    return str(chat_id) in _load("bloqueados.json")

def bloquear(chat_id, nombre, comando):
    b = _load("bloqueados.json")
    b[str(chat_id)] = {"nombre": nombre, "comando": comando, "cuando": time.time()}
    _save("bloqueados.json", b)

def desbloquear(chat_id):
    b = _load("bloqueados.json"); b.pop(str(chat_id), None); _save("bloqueados.json", b)
    i = _load("intrusos.json");  i.pop(str(chat_id), None); _save("intrusos.json", i)

# ---------- CONTADOR DE INTENTOS ----------
def _contador(chat_id):
    i = _load("intrusos.json"); data = i.get(str(chat_id))
    if not data: return 0
    if time.time() - data.get("ultimo", 0) > DIAS:
        i.pop(str(chat_id), None); _save("intrusos.json", i); return 0
    return data.get("intentos", 0)

def _sumar(chat_id, nombre):
    i = _load("intrusos.json")
    data = i.get(str(chat_id), {"intentos": 0, "nombre": nombre})
    data["intentos"] = data.get("intentos", 0) + 1
    data["ultimo"] = time.time()
    i[str(chat_id)] = data; _save("intrusos.json", i)
    return data["intentos"]

# ---------- CASTIGO: aviso → último aviso → BAN + ALERTA ----------
async def castigo(update: Update, context: ContextTypes.DEFAULT_TYPE, comando="comando admin"):
    user   = update.effective_user
    chat_id = update.effective_chat.id
    nombre = user.username or user.full_name or str(chat_id)
    intentos = _sumar(chat_id, nombre)

    if intentos == 1:
        await update.effective_message.reply_text(
            "⚠️ No tienes permisos para usar ese comando.\n"
            "Escríbele al jefe @Kraken_Diablo.\n"
            "(Aviso 1/3 — si sigues, serás bloqueado)")
    elif intentos == 2:
        await update.effective_message.reply_text(
            "⚠️⚠️ ÚLTIMO AVISO.\n"
            "Un intento más y serás bloqueado permanentemente de Kraken.\n"
            "Todo queda registrado.")
    else:
        # (B) bloqueo al cliente
        bloquear(chat_id, nombre, comando)
        try:
            await update.effective_message.reply_text("🚫 Bloqueado por intentos no autorizados.")
        except Exception:
            pass
        # (C) broadcast al imperio
        alerta = (
            "🚨 ALERTA IMPERIO 🚨\n"
            f"👤 Intruso: @{nombre} (chat_id: {chat_id})\n"
            f"🎯 Intentó usar: {comando}\n"
            "🚫 BLOQUEADO automáticamente (3 intentos)\n"
            "⚠️ Marcado SOSPECHOSO en /stats_delivery\n"
            "Kraken no se deja. 🐙"
        )
        for destino in {EMPIRE_GROUP_ID, ADMIN_CHAT_ID}:
            try:
                await context.bot.send_message(destino, alerta)
            except Exception:
                pass

# ---------- DECORADOR PARA TODOS LOS COMANDOS ADMIN ----------
def admin_only(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        if esta_bloqueado(chat_id):
            return                      # silencio total para baneados
        if es_admin(chat_id):
            return await func(update, context)
        comando = (update.effective_message.text or "").split()[0]
        await castigo(update, context, comando)
    return wrapper
