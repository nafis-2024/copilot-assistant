from abc import ABC, abstractmethod
from typing import List, Dict, Any
import requests
import json
from config import AIModelConfig

class AIModelProvider(ABC):
    """کلاس پایه برای تمام ارائه‌دهندگان مدل"""
    
    def __init__(self, config: AIModelConfig):
        self.config = config
        self.model_name = config.model_name
        self.temperature = config.temperature
        self.max_tokens = config.max_tokens
    
    @abstractmethod
    def generate_response(self, messages: List[Dict[str, str]], system_prompt: str = "") -> str:
        """تولید پاسخ از مدل"""
        pass

class OpenAIProvider(AIModelProvider):
    """ارائه‌دهنده OpenAI"""
    
    def generate_response(self, messages: List[Dict[str, str]], system_prompt: str = "") -> str:
        if not self.config.api_key:
            return "[ERROR] کلید API OpenAI تنظیم نشده است."
        
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }
        
        all_messages = []
        if system_prompt:
            all_messages.append({"role": "system", "content": system_prompt})
        all_messages.extend(messages)
        
        payload = {
            "model": self.model_name,
            "messages": all_messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }
        
        try:
            response = requests.post(
                f"{self.config.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return data["choices"][0]["message"]["content"]
            else:
                return f"[ERROR] OpenAI Error: {response.status_code} - {response.text}"
        except Exception as e:
            return f"[ERROR] اتصال به OpenAI ناموفق: {str(e)}"

class AnthropicProvider(AIModelProvider):
    """ارائه‌دهنده Anthropic (Claude)"""
    
    def generate_response(self, messages: List[Dict[str, str]], system_prompt: str = "") -> str:
        if not self.config.api_key:
            return "[ERROR] کلید API Anthropic تنظیم نشده است."
        
        headers = {
            "x-api-key": self.config.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        payload = {
            "model": self.model_name,
            "max_tokens": self.max_tokens,
            "system": system_prompt,
            "messages": messages
        }
        
        try:
            response = requests.post(
                f"{self.config.base_url}/v1/messages",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return data["content"][0]["text"]
            else:
                return f"[ERROR] Anthropic Error: {response.status_code}"
        except Exception as e:
            return f"[ERROR] اتصال به Anthropic ناموفق: {str(e)}"

class GeminiProvider(AIModelProvider):
    """ارائه‌دهنده Google Gemini"""
    
    def generate_response(self, messages: List[Dict[str, str]], system_prompt: str = "") -> str:
        if not self.config.api_key:
            return "[ERROR] کلید API Gemini تنظیم نشده است."
        
        try:
            # استفاده از Google generative AI SDK
            import google.generativeai as genai
            genai.configure(api_key=self.config.api_key)
            model = genai.GenerativeModel(self.model_name)
            
            chat_history = []
            if system_prompt:
                chat_history.append({"role": "user", "parts": [system_prompt]})
            
            for msg in messages:
                chat_history.append({"role": msg["role"], "parts": [msg["content"]]})
            
            chat = model.start_chat(history=chat_history[:-1])
            response = chat.send_message(chat_history[-1]["parts"][0])
            return response.text
        except ImportError:
            return "[ERROR] google-generativeai نصب نشده است. pip install google-generativeai"
        except Exception as e:
            return f"[ERROR] اتصال به Gemini ناموفق: {str(e)}"

class GroqProvider(AIModelProvider):
    """ارائه‌دهنده Groq"""
    
    def generate_response(self, messages: List[Dict[str, str]], system_prompt: str = "") -> str:
        if not self.config.api_key:
            return "[ERROR] کلید API Groq تنظیم نشده است."
        
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }
        
        all_messages = []
        if system_prompt:
            all_messages.append({"role": "system", "content": system_prompt})
        all_messages.extend(messages)
        
        payload = {
            "model": self.model_name,
            "messages": all_messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }
        
        try:
            response = requests.post(
                f"{self.config.base_url}/openai/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return data["choices"][0]["message"]["content"]
            else:
                return f"[ERROR] Groq Error: {response.status_code}"
        except Exception as e:
            return f"[ERROR] اتصال به Groq ناموفق: {str(e)}"

class OllamaProvider(AIModelProvider):
    """ارائه‌دهنده Ollama (محلی)"""
    
    def generate_response(self, messages: List[Dict[str, str]], system_prompt: str = "") -> str:
        all_messages = []
        if system_prompt:
            all_messages.append({"role": "system", "content": system_prompt})
        all_messages.extend(messages)
        
        payload = {
            "model": self.model_name,
            "messages": all_messages,
            "stream": False
        }
        
        try:
            response = requests.post(
                f"{self.config.base_url}/api/chat",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                return data["message"]["content"]
            else:
                return f"[ERROR] Ollama Error: {response.status_code} - آیا Ollama اجرا می‌شود؟"
        except Exception as e:
            return f"[ERROR] اتصال به Ollama ناموفق: {str(e)}. اطمینان حاصل کنید Ollama اجرا می‌شود."

def get_provider(provider_name: str, config: AIModelConfig) -> AIModelProvider:
    """دریافت ارائه‌دهنده مدل مناسب"""
    providers = {
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
        "gemini": GeminiProvider,
        "groq": GroqProvider,
        "ollama": OllamaProvider
    }
    
    provider_class = providers.get(provider_name.lower())
    if not provider_class:
        raise ValueError(f"ارائه‌دهنده نامعلوم: {provider_name}")
    
    return provider_class(config)
