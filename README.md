# DevPilot - دستیار هوش مصنوعی برای توسعه‌دهندگان

**DevPilot** یک دستیار قدرتمند و همه‌کاره برای توسعه‌دهندگان است که می‌تواند با چندین مدل هوش مصنوعی کار کند.

## ویژگی‌های اصلی

✅ **پشتیبانی از چندین مدل:**
  - OpenAI (GPT-3.5, GPT-4)
  - Anthropic Claude
  - Google Gemini
  - Groq
  - Ollama (محلی)

✅ **کار بدون حساب:**
  - تمام گفتگوها در فایل‌های محلی ذخیره می‌شوند
  - هیچ اطلاعات شخصی ارسال نمی‌شود

✅ **ورود اختیاری به حساب:**
  - امکان حفظ تنظیمات و جلسات
  - سنکرونایزه کردن بین دستگاه‌ها (در آینده)

✅ **مناسب برای برنامه‌نویسان Python:**
  - تکمیل خودکار کد
  - تشخیص و رفع خطاها
  - تولید تست‌های واحد
  - بهینه‌سازی و refactoring
  - توضیح مفاهیم برنامه‌نویسی

## نصب

### متطلبات
- Python 3.8+
- pip

### مراحل

1. **کلون کردن مخزن:**
```bash
git clone https://github.com/nafis-2024/copilot-assistant.git
cd copilot-assistant
```

2. **نصب وابستگی‌ها:**
```bash
pip install -r requirements.txt
```

3. **تنظیم کلیدهای API:**
```bash
cp .env.example .env
```

سپس `.env` را باز کنید و کلیدهای API خود را اضافه کنید.

4. **اجرا:**
```bash
python app.py
```

## نحوه استفاده

### حالت مهمان (بدون حساب)
```
python app.py
> انتخاب 1 (ورود به حالت مهمان)
> مدل را انتخاب کنید
> شروع به چت کردن!
```

### دستورات

| دستور | توضیح |
|--------|--------|
| `/help` | نمایش راهنما |
| `/models` | نمایش مدل‌های موجود |
| `/model <name>` | انتخاب مدل |
| `/sessions` | نمایش تمام جلسات |
| `/new` | جلسه جدید |
| `/load <id>` | بارگذاری جلسه |
| `/history` | نمایش تاریخچه |
| `/export` | صادر جلسه |
| `/login` | ورود به حساب |
| `/logout` | خروج از حساب |
| `/clear` | پاک کردن جلسه |
| `/delete <id>` | حذف جلسه |
| `/exit` | خروج از برنامه |

## ساختار پوشه‌ها

```
devpilot/
├── app.py              # برنامه اصلی
├── config.py           # تنظیمات
├── storage.py          # ذخیره‌سازی محلی
├── models.py           # مدل‌های هوش مصنوعی
├── requirements.txt    # وابستگی‌ها
├── .env.example        # تنظیمات API (نمونه)
└── data/
    └── guest_sessions/ # جلسات ذخیره‌شده
```

## فایل‌های ذخیره‌شده

تمام جلسات به صورت JSON ذخیره می‌شوند:

```json
{
  "session_id": "uuid-here",
  "title": "نام جلسه",
  "created_at": "2026-10-05T12:00:00",
  "updated_at": "2026-10-05T12:30:00",
  "messages": [
    {
      "role": "user",
      "content": "سؤال کاربر",
      "timestamp": "2026-10-05T12:00:10"
    },
    {
      "role": "assistant",
      "content": "پاسخ دستیار",
      "timestamp": "2026-10-05T12:00:20"
    }
  ]
}
```

## تنظیم کلیدهای API

### OpenAI
1. https://platform.openai.com/api-keys ایجاد کنید
2. کلید را کپی کنید
3. در `.env` اضافه کنید:
   ```
   OPENAI_API_KEY=sk-...
   ```

### Anthropic (Claude)
1. https://console.anthropic.com/keys ایجاد کنید
2. کلید را کپی کنید
3. در `.env` اضافه کنید:
   ```
   ANTHROPIC_API_KEY=sk-ant-...
   ```

### Google Gemini
1. https://ai.google.dev/ مراجعه کنید
2. کلید API را دریافت کنید
3. در `.env` اضافه کنید:
   ```
   GEMINI_API_KEY=AIza...
   ```

### Groq
1. https://console.groq.com/keys ایجاد کنید
2. کلید را کپی کنید
3. در `.env` اضافه کنید:
   ```
   GROQ_API_KEY=gsk_...
   ```

### Ollama (محلی)
Ollama نیازی به کلید API ندارد:
1. https://ollama.ai دانلود کنید
2. `ollama run mistral` اجرا کنید
3. DevPilot خودکار به Ollama متصل می‌شود

## توسعه‌دهندگان

با کمک‌های شما خوشحال خواهیم بود! لطفاً PR بفرستید.

## لایسنس

MIT License - برای جزئیات `LICENSE` را ببینید.

## تماس

سؤالات یا پیشنهادات؟ یک issue ایجاد کنید! 🚀
