from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any
import json
from dotenv import load_dotenv
import os

load_dotenv()

@dataclass
class AIModelConfig:
    """تنظیمات برای هر مدل هوش مصنوعی"""
    provider: str  # openai, anthropic, gemini, groq, ollama
    api_key: str = ""
    model_name: str = ""
    base_url: str = ""
    temperature: float = 0.7
    max_tokens: int = 2048

@dataclass
class AppConfig:
    """تنظیمات اصلی برنامه"""
    app_name: str = "DevPilot"
    app_version: str = "0.1.0"
    
    # مسیرهای داده
    data_dir: Path = field(default_factory=lambda: Path("data"))
    guest_dir: Path = field(default_factory=lambda: Path("data/guest_sessions"))
    config_file: Path = field(default_factory=lambda: Path("data/config.json"))
    
    # تنظیمات اکانت
    use_account: bool = False
    account_email: str = ""
    account_token: str = ""
    
    # تنظیمات مدل
    default_model: str = "openai"
    available_models: Dict[str, AIModelConfig] = field(default_factory=dict)
    
    # تنظیمات دیگر
    debug: bool = False
    max_history: int = 100
    
    def ensure_dirs(self):
        """ایجاد تمام پوشه‌های مورد نیاز"""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.guest_dir.mkdir(parents=True, exist_ok=True)
    
    def load_from_file(self):
        """بارگذاری تنظیمات از فایل JSON"""
        if self.config_file.exists():
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.use_account = data.get("use_account", False)
                    self.account_email = data.get("account_email", "")
                    self.default_model = data.get("default_model", "openai")
                    self.debug = data.get("debug", False)
            except Exception as e:
                print(f"[WARNING] خطا در بارگذاری تنظیمات: {e}")
    
    def save_to_file(self):
        """ذخیره‌سازی تنظیمات در فایل JSON"""
        self.ensure_dirs()
        try:
            data = {
                "use_account": self.use_account,
                "account_email": self.account_email,
                "default_model": self.default_model,
                "debug": self.debug
            }
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[ERROR] خطا در ذخیره‌سازی تنظیمات: {e}")
    
    def setup_models(self):
        """راه‌اندازی مدل‌های پیش‌فرض"""
        # OpenAI
        openai_key = os.getenv("OPENAI_API_KEY", "")
        self.available_models["openai"] = AIModelConfig(
            provider="openai",
            api_key=openai_key,
            model_name="gpt-3.5-turbo",
            base_url="https://api.openai.com/v1"
        )
        
        # Anthropic (Claude)
        anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")
        self.available_models["anthropic"] = AIModelConfig(
            provider="anthropic",
            api_key=anthropic_key,
            model_name="claude-3-haiku",
            base_url="https://api.anthropic.com"
        )
        
        # Google Gemini
        gemini_key = os.getenv("GEMINI_API_KEY", "")
        self.available_models["gemini"] = AIModelConfig(
            provider="gemini",
            api_key=gemini_key,
            model_name="gemini-pro",
            base_url="https://generativelanguage.googleapis.com"
        )
        
        # Groq
        groq_key = os.getenv("GROQ_API_KEY", "")
        self.available_models["groq"] = AIModelConfig(
            provider="groq",
            api_key=groq_key,
            model_name="mixtral-8x7b-32768",
            base_url="https://api.groq.com"
        )
        
        # Ollama (محلی)
        self.available_models["ollama"] = AIModelConfig(
            provider="ollama",
            api_key="",
            model_name="mistral",
            base_url="http://localhost:11434"
        )

def get_config() -> AppConfig:
    """دریافت تنظیمات اصلی برنامه"""
    config = AppConfig()
    config.ensure_dirs()
    config.load_from_file()
    config.setup_models()
    return config
