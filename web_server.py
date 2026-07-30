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
