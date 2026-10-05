import uuid
from typing import Optional, List
from config import get_config, AppConfig
from storage import LocalConversationStorage
from models import get_provider

class DevPilotAssistant:
    """دستیار هوش مصنوعی برای توسعه‌دهندگان"""
    
    SYSTEM_PROMPT_PYTHON = """شما یک دستیار توسعه‌دهنده متخصص برای Python هستید.
وظایف شما شامل:
- تکمیل خودکار کد
- تشخیص و رفع خطاها
- تولید تست‌های واحد
- بهینه‌سازی کد
- توضیح مفاهیم برنامه‌نویسی
- کمک در طراحی معماری

همیشه کد را بر اساس PEP 8 و بهترین روش‌های Python بنویسید.
به صورت پایتونی و مودانه پاسخ دهید.
"""
    
    def __init__(self):
        self.config: AppConfig = get_config()
        self.storage = LocalConversationStorage(
            base_dir=str(self.config.guest_dir)
        )
        
        self.session_id: Optional[str] = None
        self.logged_in: bool = False
        self.current_provider = None
        self._initialize()
    
    def _initialize(self):
        """راه‌اندازی اولیه برنامه"""
        print(f"\n{'='*50}")
        print(f" {self.config.app_name} v{self.config.app_version}")
        print(f"{'='*50}\n")
    
    def start_session(self, title: str = "") -> str:
        """شروع جلسه جدید"""
        self.session_id = self.storage.create_session(
            title=title or "پروژه جدید"
        )
        print(f"[INFO] جلسه شروع شد: {self.session_id[:8]}...")
        return self.session_id
    
    def login(self, email: str) -> bool:
        """ورود به حساب"""
        if not email or "@" not in email:
            print("[ERROR] ایمیل نامعتبر است.")
            return False
        
        self.config.account_email = email
        self.config.use_account = True
        self.logged_in = True
        self.config.save_to_file()
        print(f"[INFO] وارد شدید به حساب: {email}")
        return True
    
    def logout(self):
        """خروج از حساب"""
        self.config.use_account = False
        self.config.account_email = ""
        self.logged_in = False
        self.config.save_to_file()
        print("[INFO] خارج شدید از حساب.")
    
    def guest_mode(self):
        """ورود به حالت مهمان"""
        self.logged_in = False
        self.config.use_account = False
        self.config.save_to_file()
        print("[INFO] حالت مهمان فعال است. گفتگوها در محلی ذخیره می‌شوند.")
    
    def set_model(self, model_name: str) -> bool:
        """تنظیم مدل هوش مصنوعی"""
        if model_name not in self.config.available_models:
            print(f"[ERROR] مدل '{model_name}' موجود نیست.")
            self.list_available_models()
            return False
        
        self.config.default_model = model_name
        model_config = self.config.available_models[model_name]
        
        try:
            self.current_provider = get_provider(model_name, model_config)
            print(f"[INFO] مدل تغییر کرد: {model_name} ({model_config.model_name})")
            return True
        except ValueError as e:
            print(f"[ERROR] خطا در راه‌اندازی مدل: {e}")
            return False
    
    def list_available_models(self):
        """نمایش مدل‌های موجود"""
        print("\n[مدل‌های موجود]:")
        for name, config in self.config.available_models.items():
            api_status = "✓ فعال" if config.api_key else "✗ غیرفعال"
            print(f"  • {name:12} - {config.model_name:20} [{api_status}]")
        print()
    
    def chat(self, user_message: str) -> str:
        """پیام‌رسانی با دستیار"""
        if not self.session_id:
            self.start_session()
        
        # ذخیره پیام کاربر
        self.storage.save_message(self.session_id, "user", user_message)
        print(f"\n[ذخیره شد]: پیام کاربر")
        
        # دریافت تاریخچه
        messages = self.storage.get_messages(self.session_id, limit=10)
        messages = [
            {"role": msg["role"], "content": msg["content"]}
            for msg in messages
        ]
        
        # تولید پاسخ
        if not self.current_provider:
            self.set_model(self.config.default_model)
        
        if self.current_provider:
            response = self.current_provider.generate_response(
                messages=messages,
                system_prompt=self.SYSTEM_PROMPT_PYTHON
            )
        else:
            response = "[ERROR] هیچ ارائه‌دهنده مدلی تنظیم نشده است."
        
        # ذخیره پاسخ
        self.storage.save_message(self.session_id, "assistant", response)
        
        return response
    
    def show_history(self):
        """نمایش تاریخچه جلسه"""
        if not self.session_id:
            print("[ERROR] هیچ جلسه‌ای شروع نشده است.")
            return
        
        messages = self.storage.get_messages(self.session_id)
        if not messages:
            print("[INFO] هیچ پیامی وجود ندارد.")
            return
        
        print(f"\n[تاریخچه جلسه]:")
        for i, msg in enumerate(messages, 1):
            print(f"\n{i}. {msg['role'].upper()}:")
            print(f"   {msg['content'][:200]}..." if len(msg['content']) > 200 else f"   {msg['content']}")
    
    def list_sessions(self):
        """نمایش لیست جلسات"""
        sessions = self.storage.list_sessions()
        if not sessions:
            print("[INFO] هیچ جلسه‌ای وجود ندارد.")
            return
        
        print(f"\n[جلسات ({len(sessions)})]:\n")
        for i, session in enumerate(sessions, 1):
            print(f"{i}. {session['title']} ({session['message_count']} پیام)")
            print(f"   ID: {session['session_id'][:8]}...")
            print(f"   آخرین: {session['updated_at'][:10]}\n")
    
    def load_session(self, session_id: str) -> bool:
        """بارگذاری جلسه"""
        session = self.storage.load_session(session_id)
        if session["messages"] or session["session_id"] == session_id:
            self.session_id = session_id
            print(f"[INFO] جلسه بارگذاری شد: {session['title']}")
            return True
        else:
            print(f"[ERROR] جلسه پیدا نشد.")
            return False
    
    def export_session(self, format: str = "json") -> str:
        """صادرات جلسه"""
        if not self.session_id:
            return "[ERROR] هیچ جلسه‌ای شروع نشده است."
        
        return self.storage.export_session(self.session_id, format)
    
    def show_menu(self):
        """نمایش منوی اصلی"""
        print(f"\n{'='*50}")
        print("[دستورات دستیار]:")
        print("  /help           - نمایش راهنما")
        print("  /models         - نمایش مدل‌های موجود")
        print("  /model <name>   - انتخاب مدل")
        print("  /sessions       - نمایش جلسات")
        print("  /new            - جلسه جدید")
        print("  /load <id>      - بارگذاری جلسه")
        print("  /history        - نمایش تاریخچه")
        print("  /export         - صادر جلسه")
        print("  /login          - ورود به حساب")
        print("  /logout         - خروج از حساب")
        print("  /clear          - پاک کردن جلسه")
        print("  /delete <id>    - حذف جلسه")
        print("  /exit           - خروج")
        print(f"{'='*50}\n")

def main():
    """تابع اصلی برنامه"""
    assistant = DevPilotAssistant()
    
    # انتخاب حالت
    print("\n[راه‌اندازی اولیه]:")
    print("1) ورود به حالت مهمان (بدون حساب)")
    print("2) ورود به حساب")
    
    choice = input("\nانتخاب خود: ").strip()
    
    if choice == "2":
        email = input("ایمیل خود را وارد کنید: ").strip()
        assistant.login(email)
    else:
        assistant.guest_mode()
    
    # شروع جلسه
    assistant.start_session()
    
    # انتخاب مدل
    assistant.list_available_models()
    model_choice = input("مدل را انتخاب کنید [openai/anthropic/gemini/groq/ollama]: ").strip() or "openai"
    assistant.set_model(model_choice)
    
    print("\n[راه‌اندازی کامل شد. /help را بنویسید برای راهنما]\n")
    
    # حلقه اصلی
    while True:
        try:
            user_input = input("شما: ").strip()
            
            if not user_input:
                continue
            
            # دستورات خاص
            if user_input.startswith("/"):
                command = user_input.split()
                cmd = command[0].lower()
                args = " ".join(command[1:]) if len(command) > 1 else ""
                
                if cmd == "/help":
                    assistant.show_menu()
                elif cmd == "/models":
                    assistant.list_available_models()
                elif cmd == "/model":
                    if args:
                        assistant.set_model(args)
                    else:
                        print("[ERROR] نام مدل را مشخص کنید.")
                elif cmd == "/sessions":
                    assistant.list_sessions()
                elif cmd == "/new":
                    title = input("عنوان جلسه [اختیاری]: ").strip()
                    assistant.start_session(title)
                elif cmd == "/load":
                    if args:
                        assistant.load_session(args)
                    else:
                        print("[ERROR] ID جلسه را مشخص کنید.")
                elif cmd == "/history":
                    assistant.show_history()
                elif cmd == "/export":
                    format_choice = input("فرمت [json/txt]: ").strip() or "json"
                    export = assistant.export_session(format_choice)
                    print(export)
                elif cmd == "/login":
                    email = input("ایمیل: ").strip()
                    assistant.login(email)
                elif cmd == "/logout":
                    assistant.logout()
                elif cmd == "/clear":
                    if assistant.session_id:
                        assistant.storage.clear_session(assistant.session_id)
                        print("[INFO] جلسه پاک شد.")
                elif cmd == "/delete":
                    if args:
                        assistant.storage.delete_session(args)
                        print(f"[INFO] جلسه {args[:8]}... حذف شد.")
                elif cmd == "/exit" or cmd == "/quit":
                    print("[INFO] تا دیدار بعد!")
                    break
                else:
                    print("[ERROR] دستور نامعلوم. /help را بنویسید.")
            else:
                # پیام‌رسانی
                response = assistant.chat(user_input)
                print(f"\nدستیار:\n{response}\n")
        
        except KeyboardInterrupt:
            print("\n\n[INFO] برنامه متوقف شد.")
            break
        except Exception as e:
            print(f"[ERROR] خطا: {str(e)}")

if __name__ == "__main__":
    main()
