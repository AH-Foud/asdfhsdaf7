# 🤖 Bale Bot + Web Management Panel

ربات پیام‌رسان بله با پنل مدیریت تحت وب

## ✨ Features

- 🤖 **Bale Bot** — پاسخگویی خودکار با SOP
- 🎛️ **Web Dashboard** — پنل مدیریت کامل با طراحی glassmorphism
- 👥 **User Management** — مشاهده، چت و مدیریت کاربران
- 📋 **SOP System** — راهنماهای پاسخ خودکار با کلمات کلیدی
- 📊 **Analytics** — گزارش روزانه، هفتگی و کلمات پرتکرار
- 📢 **Broadcast** — ارسال همگانی پیام به کاربران
- 🎤 **Voice Messages** — ارسال و دریافت پیام صوتی
- 🎨 **Theme System** — ۶ تم رنگی + حالت شب/روز
- ⚙️ **Settings Panel** — تنظیم BOT_TOKEN و ADMIN_ID از طریق پنل

## 🚀 Quick Install (VPS)

```bash
sudo bash install.sh
```

سپس پنل در آدرس `http://SERVER_IP:5000` قابل دسترسی است.

## ⚙️ Setup

1. پنل را باز کنید
2. به صفحه **تنظیمات** (⚙️) بروید
3. توکن ربات و آیدی ادمین را وارد کنید
4. ربات را ری‌استارت کنید

## 📋 Commands

```bash
sudo systemctl status employer-panel    # وضعیت
sudo systemctl restart employer-panel   # ری‌استارت
sudo journalctl -u employer-panel -f    # لاگ‌ها
```

## 🔗 Domain Setup (Cloudflare)

1. در Cloudflare یک A Record به IP سرور اضافه کنید
2. پروکسی Cloudflare (orange cloud) را فعال کنید
3. پنل از طریق دامنه در دسترس خواهد بود
