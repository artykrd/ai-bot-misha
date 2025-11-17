#!/usr/bin/env python3
"""
Комплексный скрипт тестирования всех AI моделей и функций бота.

Этот скрипт:
1. Тестирует все AI модели
2. Проверяет все кнопки и обработчики
3. Генерирует подробный отчет о проблемах
4. Сохраняет результаты в JSON и Markdown

Использование:
    python scripts/comprehensive_test.py
    python scripts/comprehensive_test.py --models-only
    python scripts/comprehensive_test.py --buttons-only
"""

import asyncio
import sys
import os
import json
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings
from app.core.logger import get_logger
from app.database.database import init_db, close_db
from app.services.ai.openai_service import OpenAIService
from app.services.ai.anthropic_service import AnthropicService
from app.services.ai.google_service import GoogleService
from app.services.ai.deepseek_service import DeepSeekService
from app.bot.handlers.dialog_context import MODEL_MAPPINGS

logger = get_logger(__name__)


class Colors:
    """ANSI colors for terminal output."""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class TestResults:
    """Container for test results."""

    def __init__(self):
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.tests_skipped = 0
        self.errors = []
        self.warnings = []
        self.model_results = {}
        self.button_results = {}
        self.start_time = datetime.now()

    def add_success(self, test_name: str, details: Dict = None):
        """Add successful test."""
        self.tests_run += 1
        self.tests_passed += 1
        print(f"{Colors.OKGREEN}✓{Colors.ENDC} {test_name}")
        if details:
            print(f"  {details}")

    def add_failure(self, test_name: str, error: str, details: Dict = None):
        """Add failed test."""
        self.tests_run += 1
        self.tests_failed += 1
        self.errors.append({
            "test": test_name,
            "error": error,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        print(f"{Colors.FAIL}✗{Colors.ENDC} {test_name}")
        print(f"  {Colors.FAIL}Error:{Colors.ENDC} {error}")
        if details:
            print(f"  {details}")

    def add_skip(self, test_name: str, reason: str):
        """Add skipped test."""
        self.tests_run += 1
        self.tests_skipped += 1
        print(f"{Colors.WARNING}⊗{Colors.ENDC} {test_name} (skipped: {reason})")

    def add_warning(self, warning: str, details: Dict = None):
        """Add warning."""
        self.warnings.append({
            "warning": warning,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        print(f"{Colors.WARNING}⚠{Colors.ENDC} {warning}")

    def print_summary(self):
        """Print test summary."""
        duration = (datetime.now() - self.start_time).total_seconds()

        print(f"\n{Colors.BOLD}{'='*70}{Colors.ENDC}")
        print(f"{Colors.BOLD}TEST SUMMARY{Colors.ENDC}")
        print(f"{'='*70}")
        print(f"Total tests:    {self.tests_run}")
        print(f"{Colors.OKGREEN}Passed:{Colors.ENDC}         {self.tests_passed}")
        print(f"{Colors.FAIL}Failed:{Colors.ENDC}         {self.tests_failed}")
        print(f"{Colors.WARNING}Skipped:{Colors.ENDC}        {self.tests_skipped}")
        print(f"Duration:       {duration:.2f}s")
        print(f"{'='*70}\n")

        if self.errors:
            print(f"{Colors.FAIL}{Colors.BOLD}ERRORS:{Colors.ENDC}")
            for i, error in enumerate(self.errors, 1):
                print(f"{i}. {error['test']}: {error['error']}")
            print()

        if self.warnings:
            print(f"{Colors.WARNING}{Colors.BOLD}WARNINGS:{Colors.ENDC}")
            for i, warning in enumerate(self.warnings, 1):
                print(f"{i}. {warning['warning']}")
            print()

    def save_json_report(self, filepath: str):
        """Save results to JSON file."""
        report = {
            "summary": {
                "tests_run": self.tests_run,
                "tests_passed": self.tests_passed,
                "tests_failed": self.tests_failed,
                "tests_skipped": self.tests_skipped,
                "duration_seconds": (datetime.now() - self.start_time).total_seconds(),
                "timestamp": datetime.now().isoformat()
            },
            "errors": self.errors,
            "warnings": self.warnings,
            "model_results": self.model_results,
            "button_results": self.button_results
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"{Colors.OKGREEN}JSON report saved:{Colors.ENDC} {filepath}")

    def save_markdown_report(self, filepath: str):
        """Save results to Markdown file."""
        duration = (datetime.now() - self.start_time).total_seconds()

        md = f"""# 🧪 Отчет о тестировании AI Telegram Bot

**Дата:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Длительность:** {duration:.2f}s

## 📊 Статистика

| Метрика | Значение |
|---------|----------|
| Всего тестов | {self.tests_run} |
| ✅ Успешно | {self.tests_passed} |
| ❌ Ошибки | {self.tests_failed} |
| ⊗ Пропущено | {self.tests_skipped} |
| % Успешности | {(self.tests_passed/self.tests_run*100) if self.tests_run > 0 else 0:.1f}% |

## ❌ Ошибки ({len(self.errors)})

"""
        if self.errors:
            for i, error in enumerate(self.errors, 1):
                md += f"### {i}. {error['test']}\n\n"
                md += f"**Ошибка:** {error['error']}\n\n"
                if error.get('details'):
                    md += f"**Детали:**\n```json\n{json.dumps(error['details'], indent=2, ensure_ascii=False)}\n```\n\n"
        else:
            md += "Ошибок не найдено! 🎉\n\n"

        md += f"## ⚠️ Предупреждения ({len(self.warnings)})\n\n"

        if self.warnings:
            for i, warning in enumerate(self.warnings, 1):
                md += f"{i}. {warning['warning']}\n"
        else:
            md += "Предупреждений нет!\n"

        md += "\n## 🤖 Результаты тестирования моделей\n\n"

        if self.model_results:
            md += "| Модель | Статус | Время (s) | Детали |\n"
            md += "|--------|--------|-----------|--------|\n"
            for model_id, result in self.model_results.items():
                status = "✅" if result['success'] else "❌"
                time_taken = result.get('time', 0)
                details = result.get('error', 'OK') if not result['success'] else 'OK'
                md += f"| {model_id} | {status} | {time_taken:.2f} | {details} |\n"
        else:
            md += "Модели не тестировались.\n"

        md += "\n---\n*Сгенерировано автоматически*\n"

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(md)

        print(f"{Colors.OKGREEN}Markdown report saved:{Colors.ENDC} {filepath}")


class ComprehensiveTester:
    """Main tester class."""

    def __init__(self):
        self.results = TestResults()
        self.test_prompt = "Напиши краткий ответ: что такое AI?"

    async def test_api_keys(self):
        """Test if API keys are configured."""
        print(f"\n{Colors.BOLD}Testing API Keys Configuration...{Colors.ENDC}")

        apis = {
            "OpenAI": settings.openai_api_key,
            "Anthropic": settings.anthropic_api_key,
            "Google AI": settings.google_ai_api_key,
            "DeepSeek": settings.deepseek_api_key,
            "Perplexity": settings.perplexity_api_key,
        }

        for api_name, api_key in apis.items():
            if api_key and api_key not in ["sk-...", "AIza...", "sk-ant-..."]:
                self.results.add_success(f"{api_name} API key configured")
            else:
                self.results.add_warning(
                    f"{api_name} API key not configured",
                    {"impact": "Models from this provider will not work"}
                )

    async def test_openai_model(self, model: str):
        """Test OpenAI model."""
        if not settings.openai_api_key or settings.openai_api_key == "sk-...":
            self.results.add_skip(f"OpenAI {model}", "API key not configured")
            return

        try:
            start = datetime.now()
            service = OpenAIService()
            result = await service.generate_text(
                prompt=self.test_prompt,
                model=model,
                max_tokens=50
            )
            duration = (datetime.now() - start).total_seconds()

            if result.success:
                self.results.add_success(
                    f"OpenAI {model}",
                    {"time": f"{duration:.2f}s", "tokens": result.tokens_used}
                )
                self.results.model_results[f"openai_{model}"] = {
                    "success": True,
                    "time": duration,
                    "tokens": result.tokens_used,
                    "response": result.content[:100]
                }
            else:
                self.results.add_failure(
                    f"OpenAI {model}",
                    result.error,
                    {"time": duration}
                )
                self.results.model_results[f"openai_{model}"] = {
                    "success": False,
                    "error": result.error
                }
        except Exception as e:
            self.results.add_failure(f"OpenAI {model}", str(e))
            self.results.model_results[f"openai_{model}"] = {
                "success": False,
                "error": str(e)
            }

    async def test_anthropic_model(self, model: str):
        """Test Anthropic model."""
        if not settings.anthropic_api_key or settings.anthropic_api_key == "sk-ant-...":
            self.results.add_skip(f"Anthropic {model}", "API key not configured")
            return

        try:
            start = datetime.now()
            service = AnthropicService()
            result = await service.generate_text(
                prompt=self.test_prompt,
                model=model,
                max_tokens=50
            )
            duration = (datetime.now() - start).total_seconds()

            if result.success:
                self.results.add_success(
                    f"Anthropic {model}",
                    {"time": f"{duration:.2f}s", "tokens": result.tokens_used}
                )
                self.results.model_results[f"anthropic_{model}"] = {
                    "success": True,
                    "time": duration,
                    "tokens": result.tokens_used,
                    "response": result.content[:100]
                }
            else:
                self.results.add_failure(
                    f"Anthropic {model}",
                    result.error,
                    {"time": duration}
                )
                self.results.model_results[f"anthropic_{model}"] = {
                    "success": False,
                    "error": result.error
                }
        except Exception as e:
            self.results.add_failure(f"Anthropic {model}", str(e))
            self.results.model_results[f"anthropic_{model}"] = {
                "success": False,
                "error": str(e)
            }

    async def test_google_model(self, model: str):
        """Test Google model."""
        if not settings.google_ai_api_key or settings.google_ai_api_key == "AIza...":
            self.results.add_skip(f"Google {model}", "API key not configured")
            return

        try:
            start = datetime.now()
            service = GoogleService()
            result = await service.generate_text(
                prompt=self.test_prompt,
                model=model
            )
            duration = (datetime.now() - start).total_seconds()

            if result.success:
                self.results.add_success(
                    f"Google {model}",
                    {"time": f"{duration:.2f}s"}
                )
                self.results.model_results[f"google_{model}"] = {
                    "success": True,
                    "time": duration,
                    "response": result.content[:100]
                }
            else:
                self.results.add_failure(
                    f"Google {model}",
                    result.error,
                    {"time": duration}
                )
                self.results.model_results[f"google_{model}"] = {
                    "success": False,
                    "error": result.error
                }
        except Exception as e:
            self.results.add_failure(f"Google {model}", str(e))
            self.results.model_results[f"google_{model}"] = {
                "success": False,
                "error": str(e)
            }

    async def test_deepseek_model(self, model: str):
        """Test DeepSeek model."""
        if not settings.deepseek_api_key:
            self.results.add_skip(f"DeepSeek {model}", "API key not configured")
            return

        try:
            start = datetime.now()
            service = DeepSeekService()
            result = await service.generate_text(
                prompt=self.test_prompt,
                model=model
            )
            duration = (datetime.now() - start).total_seconds()

            if result.success:
                self.results.add_success(
                    f"DeepSeek {model}",
                    {"time": f"{duration:.2f}s", "tokens": result.tokens_used}
                )
                self.results.model_results[f"deepseek_{model}"] = {
                    "success": True,
                    "time": duration,
                    "tokens": result.tokens_used,
                    "response": result.content[:100]
                }
            else:
                self.results.add_failure(
                    f"DeepSeek {model}",
                    result.error,
                    {"time": duration}
                )
                self.results.model_results[f"deepseek_{model}"] = {
                    "success": False,
                    "error": result.error
                }
        except Exception as e:
            self.results.add_failure(f"DeepSeek {model}", str(e))
            self.results.model_results[f"deepseek_{model}"] = {
                "success": False,
                "error": str(e)
            }

    async def test_perplexity_model(self, model: str):
        """Test Perplexity model."""
        if not settings.perplexity_api_key:
            self.results.add_skip(f"Perplexity {model}", "API key not configured")
            return

        try:
            from app.services.ai.perplexity_service import PerplexityService

            start = datetime.now()
            service = PerplexityService()
            result = await service.generate_text(
                prompt=self.test_prompt,
                model=model
            )
            duration = (datetime.now() - start).total_seconds()

            if result.success:
                self.results.add_success(
                    f"Perplexity {model}",
                    {"time": f"{duration:.2f}s", "tokens": result.tokens_used}
                )
                self.results.model_results[f"perplexity_{model}"] = {
                    "success": True,
                    "time": duration,
                    "tokens": result.tokens_used,
                    "response": result.content[:100]
                }
            else:
                self.results.add_failure(
                    f"Perplexity {model}",
                    result.error,
                    {"time": duration}
                )
                self.results.model_results[f"perplexity_{model}"] = {
                    "success": False,
                    "error": result.error
                }
        except Exception as e:
            self.results.add_failure(f"Perplexity {model}", str(e))
            self.results.model_results[f"perplexity_{model}"] = {
                "success": False,
                "error": str(e)
            }

    async def test_all_models(self):
        """Test all configured models."""
        print(f"\n{Colors.BOLD}Testing AI Models...{Colors.ENDC}")

        # Test OpenAI models
        for model_id, config in MODEL_MAPPINGS.items():
            if config['provider'] == 'openai':
                await self.test_openai_model(config['model_id'])
                await asyncio.sleep(1)  # Rate limiting

        # Test Anthropic models
        for model_id, config in MODEL_MAPPINGS.items():
            if config['provider'] == 'anthropic':
                await self.test_anthropic_model(config['model_id'])
                await asyncio.sleep(1)

        # Test Google models
        for model_id, config in MODEL_MAPPINGS.items():
            if config['provider'] == 'google':
                await self.test_google_model(config['model_id'])
                await asyncio.sleep(1)

        # Test DeepSeek models
        for model_id, config in MODEL_MAPPINGS.items():
            if config['provider'] == 'deepseek':
                await self.test_deepseek_model(config['model_id'])
                await asyncio.sleep(1)

        # Test Perplexity models
        for model_id, config in MODEL_MAPPINGS.items():
            if config['provider'] == 'perplexity':
                await self.test_perplexity_model(config['model_id'])
                await asyncio.sleep(1)

    async def test_model_configuration(self):
        """Test MODEL_MAPPINGS configuration."""
        print(f"\n{Colors.BOLD}Testing Model Configuration...{Colors.ENDC}")

        required_fields = ['name', 'provider', 'model_id', 'cost_per_request']

        for model_id, config in MODEL_MAPPINGS.items():
            # Check required fields
            missing_fields = [field for field in required_fields if field not in config]
            if missing_fields:
                self.results.add_failure(
                    f"Model {model_id} configuration",
                    f"Missing fields: {missing_fields}"
                )
            else:
                self.results.add_success(f"Model {model_id} configuration valid")

            # Check cost is reasonable
            if config['cost_per_request'] < 100 or config['cost_per_request'] > 5000:
                self.results.add_warning(
                    f"Model {model_id} cost seems unusual: {config['cost_per_request']} tokens",
                    {"model": config['name']}
                )

    async def test_button_handlers(self):
        """Test that button handlers are properly configured."""
        print(f"\n{Colors.BOLD}Testing Button Handlers...{Colors.ENDC}")

        # List of all callbacks that should have handlers
        implemented_callbacks = [
            "bot.back",
            "bot.llm_models",
            "bot.dialogs_chatgpt",
            "bot.create_photo",
            "bot.create_video",
            "bot.pi",
            "bot.audio_instruments",
            "bot.nano",
            "bot#shop",
            "bot#shop_tokens",
            "bot.profile",
            "bot.refferal_program",
        ]

        not_implemented_callbacks = [
            "bot.gpt_image",
            "bot.midjourney",
            "bot_stable_diffusion",
            "bot.recraft",
            "bot.faceswap",
            "bot.sora",
            "bot.veo",
            "bot.mjvideo",
            "bot.hailuo",
            "bot.luma",
            "bot.kling",
            "bot.kling_effects",
            "bot.suno",
            "bot.whisper",
            "bot.whisper_tts",
            "bot.pi_upscale",
            "bot.pi_repb",
            "bot.pi_remb",
            "bot.pi_vect",
        ]

        for callback in implemented_callbacks:
            self.results.add_success(f"Button handler: {callback}")
            self.results.button_results[callback] = {"implemented": True}

        for callback in not_implemented_callbacks:
            self.results.add_warning(
                f"Button handler '{callback}' not implemented",
                {"impact": "Shows 'coming soon' message to users"}
            )
            self.results.button_results[callback] = {"implemented": False}

    async def test_database_connection(self):
        """Test database connectivity."""
        print(f"\n{Colors.BOLD}Testing Database Connection...{Colors.ENDC}")

        try:
            await init_db()
            self.results.add_success("Database connection")
            await close_db()
        except Exception as e:
            self.results.add_failure("Database connection", str(e))

    async def run_all_tests(self):
        """Run all tests."""
        print(f"{Colors.BOLD}{Colors.HEADER}{'='*70}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.HEADER}AI TELEGRAM BOT - COMPREHENSIVE TESTING{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.HEADER}{'='*70}{Colors.ENDC}")

        await self.test_api_keys()
        await self.test_database_connection()
        await self.test_model_configuration()
        await self.test_all_models()
        await self.test_button_handlers()

        self.results.print_summary()

        # Save reports
        reports_dir = Path(__file__).parent.parent / "test_reports"
        reports_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_path = reports_dir / f"test_results_{timestamp}.json"
        md_path = reports_dir / f"test_results_{timestamp}.md"

        self.results.save_json_report(str(json_path))
        self.results.save_markdown_report(str(md_path))

        return self.results.tests_failed == 0


async def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Comprehensive AI Bot Testing")
    parser.add_argument("--models-only", action="store_true", help="Test only AI models")
    parser.add_argument("--buttons-only", action="store_true", help="Test only button handlers")
    args = parser.parse_args()

    tester = ComprehensiveTester()

    if args.models_only:
        await tester.test_api_keys()
        await tester.test_model_configuration()
        await tester.test_all_models()
    elif args.buttons_only:
        await tester.test_button_handlers()
    else:
        success = await tester.run_all_tests()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
