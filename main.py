import os, requests
from telegram import Update
from telegram.ext import (ApplicationBuilder, CommandHandler, MessageHandler,
                          filters, ContextTypes)
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

async def chat_with_ai(user_text=None, chat_id=None, *a, **k):
    import json as _json, os as _os, urllib.request as _ur
    if not isinstance(user_text, str):
        user_text = str(user_text)
    key = _os.environ.get("GROQ_API_KEY", "")
    if not key:
        try:
            for _ln in open(_os.path.expanduser("~/.kraken_env")):
                if _ln.startswith("GROQ_API_KEY="):
                    key = _ln.split("=", 1)[1].strip().strip(chr(34)).strip(chr(39))
        except Exception:
            pass
    if not key:
        return "🔑 El cerebro Kraken esta sin llave. Avisa a papá."
    for _model in ("openai/gpt-oss-120b", "openai/gpt-oss-20b"):
        _body = _json.dumps({
            "model": _model,
            "messages": [
                {"role": "system", "content": "Eres KRAKEN-SAPIENS, asistente de Felipe Batista. Español panameño, directo, emojis de pulpo."},
                {"role": "user", "content": user_text}
            ]}).encode()
        _req = _ur.Request("https://api.groq.com/openai/v1/chat/completions", data=_body,
            headers={"Authorization": "Bearer " + key,
                     "Content-Type": "application/json",
                     "User-Agent": "Mozilla/5.0 (Linux; Android 13) Kraken/1.0"})
        try:
            _d = _json.loads(_ur.urlopen(_req, timeout=60).read())
            _ch = _d.get("choices") or []
            if _ch:
                _txt = _ch[0].get("message", {}).get("content", "")
                if _txt:
                    return _txt
        except Exception:
            continue
    return "🐙 El cerebro esta descansando un momento. Intenta de nuevo, papá."

import json
from telegram.ext import filters as _flt
ADMIN_ID = 8707507405
FAM_KEY = '7790hijomio'
PRODUCTOS = {'Asesoría 1-a-1': 50, 'Señales Crypto': 100, 'Bot Personalizado': 300, 'Token Personalizado': 500, 'Pack Imperio': 800}
WALLETS_TXT = '₿ BTC bc1qwpktag36yacv6z7eqy6exz4j0vstwa7shzam29 · 🔷 BNB 0xA36A3493cB08faDeBEF40ab68Fd8A71EcB6A4416 · 🟣 TRON USDT TYXe6hXkkeevLsQsrCbTWgwfBq2RL1KNjh · 📱 Yappy'
def _load(f, d):
    try:
        return json.load(open(f))
    except Exception:
        return d
def _save(f, d):
    try:
        json.dump(d, open(f, 'w'))
    except Exception:
        pass
def _nivel(chat_id):
    if chat_id == ADMIN_ID:
        return 'DIOS'
    if str(chat_id) in _load('familia.json', {}):
        return 'HIERRO'
    return 'CLIENTE'
def _es_admin(chat_id):
    return _nivel(chat_id) in ('DIOS', 'HIERRO')
def _castigo(chat_id, username, cmd):
    blo = _load('bloqueados.json', {})
    if str(chat_id) in blo:
        return 'BLOQUEADO'
    intr = _load('intrusos.json', {})
    n = int(intr.get(str(chat_id), 0)) + 1
    intr[str(chat_id)] = n
    _save('intrusos.json', intr)
    if n >= 3:
        blo[str(chat_id)] = {'user': username, 'cmd': cmd}
        _save('bloqueados.json', blo)
        return 'BAN'
    return 'AVISO2' if n == 2 else 'AVISO1'
async def _negar(c, u, cmd):
    r = _castigo(u.effective_chat.id, u.effective_user.username or str(u.effective_user.id), cmd)
    if r == 'BLOQUEADO':
        return
    if r == 'BAN':
        await c.bot.send_message(u.effective_chat.id, '🚫 Bloqueado por intentos no autorizados.')
        await c.bot.send_message(ADMIN_ID, '🚨 ALERTA IMPERIO 🚨 👤 Intruso: @' + str(u.effective_user.username) + ' (' + str(u.effective_chat.id) + ') 🎯 Intentó: ' + cmd + ' 🚫 BLOQUEADO (3 intentos). Kraken no se deja. 🐙')
        return
    if r == 'AVISO2':
        await c.bot.send_message(u.effective_chat.id, '⚠️⚠️ ÚLTIMO AVISO. Un intento más y serás bloqueado permanentemente de Kraken. Todo queda registrado.')
        return
    await c.bot.send_message(u.effective_chat.id, '⚠️ No tienes permisos para usar ese comando. Escríbele al jefe @Kraken_Diablo. (Aviso 1/3)')
async def h_start(u, c):
    await c.bot.send_message(u.effective_chat.id, '🐙⚡ ¡KRAKEN VIVO! 🐙💎\n\nEscribe /comandos para ver el imperio.\n🛒 /catalogo · 🛍️ /comprar · 📦 /estado')
async def h_comandos(u, c):
    t = '📋 COMANDOS KRAKEN 🐙\n\n🛒 TIENDA: /catalogo · /comprar <producto> · /estado · /comandos'
    if _es_admin(u.effective_chat.id):
        t += '\n\n👑 ADMIN: /pedidos · /approve <id> · /construir <id> · /entregar <id> · /wallets · /unban <id>\n🛵 DELIVERY: /alta_local · /alta_rider · /pedidos_delivery · /zonas · /comisiones · /stats_delivery · /pagar_rider · /pagar_local\n🔥 /reclutar'
    await c.bot.send_message(u.effective_chat.id, t)
async def h_catalogo(u, c):
    t = '🛒 CATÁLOGO KRAKEN IMPERIO 🐙💎\n\n'
    for k, v in PRODUCTOS.items():
        t += '📦 ' + k + ' — $' + str(v) + ' USDT\n'
    t += '\n🛵 KRAKEN DELIVERY: escribe /delivery\n🛒 Comprar: /comprar <producto>'
    await c.bot.send_message(u.effective_chat.id, t)
async def h_comprar(u, c):
    p = (u.message.text or '').split(maxsplit=1)
    if len(p) < 2:
        await c.bot.send_message(u.effective_chat.id, '🛒 Usa: /comprar <producto>\nEj: /comprar Asesoría 1-a-1\nMira /catalogo')
        return
    prod, price = p[1].strip(), None
    for k, v in PRODUCTOS.items():
        if k.lower() in prod.lower() or prod.lower() in k.lower():
            prod, price = k, v
            break
    if price is None:
        await c.bot.send_message(u.effective_chat.id, '❌ Producto no encontrado. Mira /catalogo')
        return
    o = _load('orders.json', {})
    oid = '#K-' + str(1001 + len(o))
    o[oid] = {'chat_id': u.effective_chat.id, 'user': u.effective_user.username or str(u.effective_user.id), 'product': prod, 'price': price, 'status': 'PENDIENTE DE PAGO'}
    _save('orders.json', o)
    await c.bot.send_message(u.effective_chat.id, '🛒 PEDIDO CREADO ' + oid + '\n📦 ' + prod + ' — $' + str(price) + ' USDT\n\n💰 PAGA AQUÍ:\n' + WALLETS_TXT + '\n\n📸 Manda tu comprobante y escribe /estado. El jefe lo aprueba 🐙')
    await c.bot.send_message(ADMIN_ID, '🛒 NUEVO PEDIDO ' + oid + '\n👤 @' + str(o[oid]['user']) + ' (' + str(u.effective_chat.id) + ')\n📦 ' + prod + ' — $' + str(price) + ' USDT')
async def h_estado(u, c):
    o, uid = _load('orders.json', {}), u.effective_chat.id
    if not o:
        await c.bot.send_message(uid, '📦 No hay pedidos todavía. Usa /comprar 🛒')
        return
    t = '📦 PEDIDOS KRAKEN 🐙\n\n'
    for k, v in o.items():
        if _es_admin(uid) or v.get('chat_id') == uid:
            t += k + ' · ' + str(v.get('product')) + ' · $' + str(v.get('price')) + ' · ' + str(v.get('status')) + '\n'
    await c.bot.send_message(uid, t)
async def h_pedidos(u, c):
    if not _es_admin(u.effective_chat.id):
        await _negar(c, u, '/pedidos')
        return
    o = _load('orders.json', {})
    t = '📋 TABLERO IMPERIAL 🐙\n\n'
    for k, v in o.items():
        t += k + ' · @' + str(v.get('user')) + ' · ' + str(v.get('product')) + ' · $' + str(v.get('price')) + ' · ' + str(v.get('status')) + '\n'
    await c.bot.send_message(u.effective_chat.id, t or '📋 Sin pedidos')
def _oid(parts):
    if len(parts) < 2:
        return None
    x = parts[1].strip()
    return x if x.startswith('#K-') else '#K-' + x.lstrip('#')
async def h_approve(u, c):
    if not _es_admin(u.effective_chat.id):
        await _negar(c, u, '/approve')
        return
    oid = _oid((u.message.text or '').split())
    o = _load('orders.json', {})
    if not oid or oid not in o:
        await c.bot.send_message(u.effective_chat.id, '❌ Pedido no encontrado. Uso: /approve #K-1001')
        return
    o[oid]['status'] = 'APROBADO'
    _save('orders.json', o)
    await c.bot.send_message(o[oid].get('chat_id'), '✅ Pago aprobado, tu asesoría/bot/token ya está en construcción 🔨')
    await c.bot.send_message(u.effective_chat.id, '✅ ' + oid + ' APROBADO · cliente notificado')
async def h_construir(u, c):
    if not _es_admin(u.effective_chat.id):
        await _negar(c, u, '/construir')
        return
    oid = _oid((u.message.text or '').split())
    o = _load('orders.json', {})
    if not oid or oid not in o:
        await c.bot.send_message(u.effective_chat.id, '❌ Pedido no encontrado. Uso: /construir #K-1001')
        return
    o[oid]['status'] = 'EN CONSTRUCCIÓN'
    _save('orders.json', o)
    await c.bot.send_message(u.effective_chat.id, '🔨 ' + oid + ' EN CONSTRUCCIÓN')
async def h_entregar(u, c):
    if not _es_admin(u.effective_chat.id):
        await _negar(c, u, '/entregar')
        return
    p = (u.message.text or '').split(maxsplit=2)
    oid = _oid(p)
    o = _load('orders.json', {})
    if not oid or oid not in o:
        await c.bot.send_message(u.effective_chat.id, '❌ Pedido no encontrado. Uso: /entregar #K-1001 <entregable>')
        return
    extra = p[2] if len(p) > 2 else 'Tu pedido fue entregado 🐙🔥 Escríbele al jefe @Kraken_Diablo por cualquier detalle.'
    o[oid]['status'] = 'ENTREGADO'
    _save('orders.json', o)
    await c.bot.send_message(o[oid].get('chat_id'), '🚀 ENTREGA ' + oid + '\n\n' + extra)
    await c.bot.send_message(u.effective_chat.id, '🚀 ' + oid + ' ENTREGADO · cliente notificado')
async def h_wallets(u, c):
    if not _es_admin(u.effective_chat.id):
        await _negar(c, u, '/wallets')
        return
    await c.bot.send_message(u.effective_chat.id, '💰 WALLETS IMPERIO 🐙\n' + WALLETS_TXT)
async def h_texto(u, c):
    uid = u.effective_chat.id
    text = (u.message.text or '')
    if text.strip() == FAM_KEY:
        fam = _load('familia.json', {})
        fam[str(uid)] = u.effective_user.username or str(uid)
        _save('familia.json', fam)
        await c.bot.send_message(uid, '🔵 MODO HIERRO ACTIVADO, mi rey 🔥🐙')
        return
    if str(uid) in _load('bloqueados.json', {}):
        return
    try:
        r = await chat_with_ai(text, uid)
    except Exception:
        r = '🐙 El cerebro esta descansando un momento. Intenta de nuevo, papá.'
    await c.bot.send_message(uid, r)
HANDLERS = [
    ('start', CommandHandler('start', h_start)),
    ('comandos', CommandHandler('comandos', h_comandos)),
    ('catalogo', CommandHandler('catalogo', h_catalogo)),
    ('comprar', CommandHandler('comprar', h_comprar)),
    ('estado', CommandHandler('estado', h_estado)),
    ('pedidos', CommandHandler('pedidos', h_pedidos)),
    ('approve', CommandHandler('approve', h_approve)),
    ('construir', CommandHandler('construir', h_construir)),
    ('entregar', CommandHandler('entregar', h_entregar)),
    ('wallets', CommandHandler('wallets', h_wallets)),
    ('texto', MessageHandler(_flt.TEXT & ~_flt.COMMAND, h_texto)),
]

def _kraken_arranque():
    import asyncio as _aio
    from telegram.ext import ApplicationBuilder
    _aio.set_event_loop(_aio.new_event_loop())
    app = ApplicationBuilder().token("8611511853:AAFYjCw99khwCKwd180zHDraWj7_diBHIZg").build()
    for _n, _h in (getattr(_MOD, "HANDLERS", []) or []):
        app.add_handler(_h)
    print("🐙⚡ KRAKEN VIVO — polling imperial activo")
    app.run_polling()

if __name__ == "__main__":
    try:
        import sys as _sys
        _MOD = _sys.modules.get(__name__)
        if not getattr(_MOD, "HANDLERS", None):
            print("OJO: no hay lista HANDLERS — registrando handlers sueltos")
        _kraken_arranque()
    except Exception as _e:
        import traceback as _tb
        _tb.print_exc()
        print("💀 KRAKEN NO ARRANCA:", _e)
