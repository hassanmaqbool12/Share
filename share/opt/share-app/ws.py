import asyncio
import threading
from aiohttp import web
from typing import Set
import logging
import bridge

app = bridge.start()
data = app.data1
# -------------------------------------------------------------------
# Logging
# -------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("ws-server")

# -------------------------------------------------------------------
# Globals (thread-safe)
# -------------------------------------------------------------------
clients: Set[web.WebSocketResponse] = set()
clients_lock = threading.Lock()

# The aiohttp server uses a dedicated event loop.
# We create it *before* starting the thread so it is non-optional.
server_loop: asyncio.AbstractEventLoop = asyncio.new_event_loop()

# -------------------------------------------------------------------
# Aiohttp App
# -------------------------------------------------------------------
app = web.Application()

async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    # Add client safely
    with clients_lock:
        clients.add(ws)

    try:
        async for msg in ws:
            if msg.type == web.WSMsgType.TEXT:
                if msg.data in data.ALLOWED:
                    data.ONLINE.append([msg.data, "Android", ws])
            elif msg.type == web.WSMsgType.ERROR:
                pass
    finally:
        # Remove safely
        with clients_lock:
            clients.discard(ws)
        await ws.close()

    return ws


app.router.add_get("/ws", websocket_handler)

# -------------------------------------------------------------------
# Aiohttp Thread Worker
# -------------------------------------------------------------------
def start_aiohttp():
    asyncio.set_event_loop(server_loop)

    runner = web.AppRunner(app)
    server_loop.run_until_complete(runner.setup())

    site = web.TCPSite(runner, "0.0.0.0", 5001)
    server_loop.run_until_complete(site.start())
    server_loop.run_forever()

# Start the thread
threading.Thread(target=start_aiohttp, daemon=True).start()

# -------------------------------------------------------------------
# Broadcast Function
# -------------------------------------------------------------------
def broadcast_message(msg: str):
    """
    Broadcast a message to all connected websocket clients
    from ANY thread safely.
    """
    with clients_lock:
        active_clients = list(clients)

    log.info(f"[BROADCAST] Sending to {len(active_clients)} clients")

    for ws in active_clients:
        # Submit coroutine to the correct loop
        asyncio.run_coroutine_threadsafe(
            ws.send_str(msg),
            server_loop
        )

# -------------------------------------------------------------------
# Example high-level wrapper (replaced `wio` logic)
# -------------------------------------------------------------------
def askDownload(msg: str):
    try:
        broadcast_message(msg)
        print("Request Sent to " + msg.split(" ")[0])
        return True
    except Exception as e:
        print("Error:", e)
        print(msg.split(" ")[1] + " is offline")
        return False
