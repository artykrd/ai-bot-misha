#!/usr/bin/env python3
"""
Интерактивный тестер AI моделей.

Позволяет быстро протестировать любую модель с произвольным запросом.

Использование:
    python scripts/interactive_model_test.py
    python scripts/interactive_model_test.py --model gpt-4o-mini
    python scripts/interactive_model_test.py --model claude-3-5-sonnet --prompt "Расскажи про Python"
"""

import asyncio
import sys
from pathlib import Path
from typing import Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings
from app.services.ai.openai_service import OpenAIService
from app.services.ai.anthropic_service import AnthropicService
from app.services.ai.google_service import GoogleService
from app.services.ai.deepseek_service import DeepSeekService
from app.bot.handlers.dialog_context import MODEL_MAPPINGS


class InteractiveModelTester:
    """Interactive model testing tool."""

    def __init__(self):
        self.services = {
            'openai': OpenAIService() if settings.openai_api_key else None,
            'anthropic': AnthropicService() if settings.anthropic_api_key else None,
            'google': GoogleService() if settings.google_ai_api_key else None,
            'deepseek': DeepSeekService() if settings.deepseek_api_key else None,
        }

    def print_available_models(self):
        """Print all available models."""
        print("\n📋 Доступные модели:\n")

        providers = {}
        for model_id, config in MODEL_MAPPINGS.items():
            provider = config['provider']
            if provider not in providers:
                providers[provider] = []
            providers[provider].append({
                'id': model_id,
                'name': config['name'],
                'model_id': config['model_id'],
                'cost': config['cost_per_request']
            })

        for provider, models in providers.items():
            service_available = self.services.get(provider) is not None
            status = "✅" if service_available else "❌"
            print(f"\n{status} {provider.upper()}:")
            for model in models:
                print(f"  {model['id']}: {model['name']}")
                print(f"     Model ID: {model['model_id']}")
                print(f"     Cost: {model['cost']} tokens")

    async def test_model(self, model_id: str, prompt: str):
        """Test specific model."""
        config = MODEL_MAPPINGS.get(model_id)
        if not config:
            print(f"❌ Модель {model_id} не найдена!")
            return

        provider = config['provider']
        model_name = config['model_id']
        service = self.services.get(provider)

        if not service:
            print(f"❌ Сервис {provider} не настроен (отсутствует API ключ)")
            return

        print(f"\n🤖 Тестирование: {config['name']}")
        print(f"   Provider: {provider}")
        print(f"   Model: {model_name}")
        print(f"   Cost: {config['cost_per_request']} tokens")
        print(f"\n📝 Промпт: {prompt}\n")
        print("⏳ Отправка запроса...\n")

        try:
            result = await service.generate_text(
                prompt=prompt,
                model=model_name,
                system_prompt=config.get('system_prompt')
            )

            if result.success:
                print(f"✅ Успешно!")
                print(f"⏱️  Время: {result.processing_time:.2f}s")
                if result.tokens_used:
                    print(f"🎫 Токенов использовано: {result.tokens_used}")
                print(f"\n{'='*70}")
                print(f"📄 ОТВЕТ:")
                print(f"{'='*70}")
                print(result.content)
                print(f"{'='*70}\n")
            else:
                print(f"❌ Ошибка!")
                print(f"⚠️  {result.error}\n")

        except Exception as e:
            print(f"❌ Исключение: {str(e)}\n")

    async def interactive_mode(self):
        """Run in interactive mode."""
        print("\n" + "="*70)
        print("🧪 ИНТЕРАКТИВНЫЙ ТЕСТЕР AI МОДЕЛЕЙ")
        print("="*70)

        self.print_available_models()

        while True:
            print("\n" + "-"*70)
            model_id = input("\n🔢 Введите ID модели (или 'list' для списка, 'quit' для выхода): ").strip()

            if model_id.lower() == 'quit':
                print("\n👋 До свидания!")
                break

            if model_id.lower() == 'list':
                self.print_available_models()
                continue

            try:
                model_id = int(model_id)
            except ValueError:
                print("❌ Неверный формат! Введите числовой ID модели.")
                continue

            if model_id not in MODEL_MAPPINGS:
                print(f"❌ Модель {model_id} не найдена!")
                continue

            prompt = input("\n📝 Введите промпт: ").strip()
            if not prompt:
                print("❌ Промпт не может быть пустым!")
                continue

            await self.test_model(model_id, prompt)

            again = input("\n🔄 Протестировать еще одну модель? (y/n): ").strip().lower()
            if again != 'y':
                print("\n👋 До свидания!")
                break

    async def quick_test(self, model_id: Optional[int] = None, prompt: Optional[str] = None):
        """Quick test mode."""
        if not model_id:
            self.print_available_models()
            return

        if not prompt:
            prompt = "Напиши краткий ответ: что такое AI?"

        await self.test_model(model_id, prompt)


async def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Interactive AI Model Tester")
    parser.add_argument("--model", type=int, help="Model ID to test")
    parser.add_argument("--prompt", type=str, help="Prompt to send")
    parser.add_argument("--list", action="store_true", help="List all available models")
    args = parser.parse_args()

    tester = InteractiveModelTester()

    if args.list:
        tester.print_available_models()
    elif args.model:
        await tester.quick_test(args.model, args.prompt)
    else:
        await tester.interactive_mode()


if __name__ == "__main__":
    asyncio.run(main())
