# -*- coding: utf-8 -*-
# وب سرور + API + پنل مدیریت
# اجرا: python web_server.py

import json, os, time, threading
from datetime import datetime
import aiofiles

import config
import bot_core
from analytics import Analytics

analytics_bot = bot_core.analytics

# ===================== FastAPI =====================
from fastapi import FastAPI, HTTPException, Query, UploadFile, File, Form
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="پنل مدیریت ربات بله", version="2.1")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# ===================== API =====================

@app.get("/api/status")
def api_status():
    registered = bot_core.load_registered()
    sops = bot_core.load_sops()
    msgs = analytics_bot._load()
    return {
        "online": True,
        "bot_configured": bool(config.BOT_TOKEN),
        "bot_token": config.BOT_TOKEN[:12] + "..." if config.BOT_TOKEN else "تنظیم نشده",
        "admin_id": config.ADMIN_ID,
        "total_users": len(registered),
        "total_sops": len(sops),
        "total_messages": len(msgs),
        "last_updated": datetime.now().isoformat()
    }

@app.get("/api/stats")
def api_stats():
    daily = analytics_bot.get_daily_stats()
    weekly = analytics_bot.get_weekly_report()
    registered = bot_core.load_registered()
    sops = bot_core.load_sops()
    msgs = analytics_bot._load()
    msgs_sorted = sorted(msgs, key=lambda m: m.get("timestamp", ""), reverse=True)
    return {
        "daily": daily,
        "weekly": weekly,
        "users_count": len(registered),
        "sops_count": len(sops),
        "messages_count": len(msgs),
        "last_message": msgs_sorted[0] if msgs_sorted else None
    }

@app.get("/api/messages")
def api_messages(limit: int = 100, offset: int = 0, user_id: str = None):
    msgs = analytics_bot._load()
    if user_id:
        msgs = [m for m in msgs if str(m.get("user_id")) == str(user_id)]
    msgs.sort(key=lambda m: m.get("timestamp", ""), reverse=True)
    result = msgs[offset:offset + limit]
    return {"messages": result, "total": len(msgs), "has_more": (offset + limit) < len(msgs)}

@app.get("/api/conversation/{user_id}")
def api_conversation(user_id: str):
    conv = analytics_bot.get_user_conversation(user_id)
    user_info = bot_core.load_registered().get(user_id, {})
    return {"user_id": user_id, "user_name": user_info.get("first_name", "ناشناس"), "phone": user_info.get("phone", ""), "messages": conv}

@app.get("/api/users")
def api_users():
    registered = bot_core.load_registered()
    users = []
    for uid, info in registered.items():
        msgs = analytics_bot._load()
        user_msgs = sum(1 for m in msgs if str(m.get("user_id")) == uid)
        last_msg = None
        for m in reversed(msgs):
            if str(m.get("user_id")) == uid:
                last_msg = m
                break
        users.append({
            "user_id": uid,
            "first_name": info.get("first_name", "کاربر"),
            "phone": info.get("phone", ""),
            "registered_at": info.get("registered_at", ""),
            "total_messages": user_msgs,
            "last_message": last_msg["text"][:80] if last_msg else "",
            "last_message_time": last_msg["timestamp"] if last_msg else ""
        })
    users.sort(key=lambda u: u.get("registered_at", ""), reverse=True)
    return {"users": users, "total": len(users)}

@app.get("/api/sops")
def api_sops():
    return {"sops": bot_core.load_sops()}

@app.post("/api/sops")
def api_add_sop(data: dict):
    name = data.get("name", "").strip()
    response = data.get("response", "").strip()
    if len(name) < 2 or len(response) < 5:
        raise HTTPException(400, "نام و پاسخ SOP معتبر نیست")
    sop = bot_core.add_sop(name, response, data.get("keywords", ""))
    return {"ok": True, "sop": sop}

@app.put("/api/sops/{sop_id}")
def api_update_sop(sop_id: int, data: dict):
    sop = bot_core.update_sop(sop_id, data.get("name"), data.get("response"), data.get("keywords"), data.get("smart_enabled"))
    if not sop:
        raise HTTPException(404, "SOP یافت نشد")
    return {"ok": True, "sop": sop}

@app.delete("/api/sops/{sop_id}")
def api_delete_sop(sop_id: int):
    if bot_core.delete_sop(sop_id):
        return {"ok": True}
    raise HTTPException(404, "SOP یافت نشد")

@app.delete("/api/users/{user_id}")
def api_delete_user(user_id: str):
    registered = bot_core.load_registered()
    if user_id not in registered:
        raise HTTPException(404, "کاربر یافت نشد")
    name = registered[user_id].get("first_name", "کاربر")
    bot_core.unregister_user(user_id)
    return {"ok": True, "message": f"{name} حذف شد"}

@app.post("/api/reply")
def api_reply(data: dict):
    user_id = str(data.get("user_id", ""))
    text = data.get("text", "").strip()
    if not user_id or not text:
        raise HTTPException(400, "اطلاعات ناقص")
    ok, msg = bot_core.reply_to_user(user_id, text)
    if ok:
        return {"ok": True, "message": msg}
    raise HTTPException(400, msg)

@app.post("/api/broadcast")
def api_broadcast(data: dict):
    text = data.get("text", "").strip()
    targets = data.get("targets", [])
    if len(text) < 2:
        raise HTTPException(400, "متن پیام کوتاه است")
    sent = bot_core.broadcast_message(targets if targets else None, text)
    return {"ok": True, "sent": sent}

@app.post("/api/broadcast-sop")
def api_broadcast_sop(data: dict):
    sop_id = data.get("sop_id", 0)
    targets = data.get("targets", [])
    sent = bot_core.broadcast_sop(sop_id, targets if targets else None)
    return {"ok": True, "sent": sent}

@app.get("/api/voice-url/{file_id}")
def api_voice_url(file_id: str):
    url = bot_core.get_voice_file_url(file_id)
    if url:
        return {"url": url}
    raise HTTPException(404, "فایل صوتی یافت نشد")

@app.get("/api/voice-proxy/{file_id}")
def api_voice_proxy(file_id: str):
    import requests as req_lib
    file_path_obj = bot_core.api_request("getFile", {"file_id": file_id})
    if not file_path_obj or "file_path" not in file_path_obj:
        raise HTTPException(404, "فایل یافت نشد")
    fp = file_path_obj["file_path"]
    file_url = f"https://tapi.bale.ai/file/bot{config.BOT_TOKEN}/{fp}"
    try:
        resp = req_lib.get(file_url, timeout=30)
        if resp.status_code == 200:
            ct = resp.headers.get("content-type", "")
            if not ct or ct == "application/octet-stream":
                ext = fp.split(".")[-1].lower() if "." in fp else ""
                ct_map = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png", "gif": "image/gif", "webp": "image/webp", "ogg": "audio/ogg", "oga": "audio/ogg", "mp3": "audio/mpeg", "mp4": "video/mp4", "pdf": "application/pdf", "zip": "application/zip", "doc": "application/msword", "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}
                ct = ct_map.get(ext, "application/octet-stream")
            return Response(content=resp.content, media_type=ct)
    except Exception as e:
        print(f"[File Proxy] Error: {e}")
    raise HTTPException(502, "خطا در دریافت فایل")

# ===================== تنظیمات (Settings) =====================

@app.get("/api/settings")
def api_get_settings():
    return {
        "bot_token": config.BOT_TOKEN[:12] + "..." if config.BOT_TOKEN else "",
        "bot_token_full": config.BOT_TOKEN,
        "admin_id": config.ADMIN_ID,
        "web_host": config.WEB_HOST,
        "web_port": config.WEB_PORT,
        "is_configured": bool(config.BOT_TOKEN)
    }

@app.post("/api/settings")
def api_save_settings(data: dict):
    bot_token = data.get("bot_token", "").strip()
    admin_id = data.get("admin_id", "")
    if not bot_token:
        raise HTTPException(400, "توکن ربات الزامی است")
    if not admin_id:
        raise HTTPException(400, "آیدی ادمین الزامی است")
    try:
        admin_id = int(admin_id)
    except (ValueError, TypeError):
        raise HTTPException(400, "آیدی ادمین باید عدد باشد")
    config.save_settings({"bot_token": bot_token, "admin_id": admin_id})
    return {"ok": True, "message": "تنظیمات با موفقیت ذخیره شد. لطفاً ربات را ری‌استارت کنید."}

# ===================== داشبورد =====================

DASHBOARD_HTML_PATH = "dashboard.html"
DASHBOARD_HTML = ""

def get_dashboard_html():
    global DASHBOARD_HTML
    if not DASHBOARD_HTML:
        try:
            with open(DASHBOARD_HTML_PATH, "r", encoding="utf-8") as f:
                DASHBOARD_HTML = f.read()
        except FileNotFoundError:
            DASHBOARD_HTML = "<html><body><h1>Dashboard file not found</h1></body></html>"
    return DASHBOARD_HTML


@app.get("/", response_class=HTMLResponse)
async def dashboard():
    return HTMLResponse(content=get_dashboard_html())

@app.get("/health")
async def health():
    return {"status": "ok", "time": datetime.now().isoformat()}


# ===================== BOT POLLING =====================