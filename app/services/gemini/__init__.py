from app.services.gemini.executor import GeminiExecutionLayer, gemini_executor

# Alias for services that import the old name
gemini_execution_layer = gemini_executor

__all__ = ["GeminiExecutionLayer", "gemini_executor", "gemini_execution_layer"]
