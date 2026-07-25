"""
Gemini Service for stream generation using Google Gemini API with automatic model fallbacks and robust error handling.
"""
import time
import logging
from typing import AsyncGenerator
from google import genai
from google.genai.errors import APIError, ClientError
from app.core.config import get_settings

logger = logging.getLogger(__name__)

# Candidate models in order of instant availability
FALLBACK_MODELS = [
    "gemini-flash-latest",
    "gemini-2.0-flash-lite",
    "gemini-2.5-flash",
    "gemini-pro-latest",
]


class GeminiService:
    """Service class for interacting with Google Gemini API with token streaming, model fallbacks, and retries."""

    def _get_client_and_model(self) -> tuple[genai.Client | None, str, str]:
        settings = get_settings()
        api_key = settings.gemini_api_key.strip() if settings.gemini_api_key else ""
        model_name = settings.gemini_model_name or "gemini-flash-latest"
        if not api_key:
            return None, model_name, ""
        return genai.Client(api_key=api_key), model_name, api_key

    async def generate_stream(self, prompt: str) -> AsyncGenerator[str, None]:
        """Streams response tokens from Gemini API asynchronously with automatic model fallback."""
        client, primary_model, api_key = self._get_client_and_model()

        if not client or not api_key:
            logger.error("Attempted Gemini API call without configured GEMINI_API_KEY.")
            yield "GEMINI_API_KEY is not configured on the server. Please add your key to backend/.env file."
            return

        # Prepare candidate list starting with primary model
        candidate_models = [primary_model] + [m for m in FALLBACK_MODELS if m != primary_model]

        start_time = time.perf_counter()
        stream_started = False
        token_count = 0

        for model_candidate in candidate_models:
            logger.info(f"Attempting stream generation with Gemini model candidate '{model_candidate}'...")
            try:
                response_stream = client.models.generate_content_stream(
                    model=model_candidate,
                    contents=prompt,
                )

                for chunk in response_stream:
                    if chunk.text:
                        token_count += 1
                        stream_started = True
                        yield chunk.text

                if stream_started:
                    elapsed_sec = time.perf_counter() - start_time
                    logger.info(
                        f"Gemini stream completed using '{model_candidate}' in {elapsed_sec:.2f}s "
                        f"(Received ~{token_count} chunks/tokens)."
                    )
                    return

            except (APIError, ClientError) as e:
                error_str = str(e)
                logger.warning(f"Gemini API error on model '{model_candidate}': {error_str[:120]}")

                if stream_started:
                    yield f"\n[Stream interrupted from {model_candidate}]"
                    return

                if "404" in error_str or "NOT_FOUND" in error_str or "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                    logger.info(f"Model '{model_candidate}' returned error. Trying next fallback candidate...")
                    continue

            except Exception as e:
                logger.error(f"Unexpected error on model '{model_candidate}': {str(e)}", exc_info=True)
                if stream_started:
                    yield f"\n[Stream error: {str(e)}]"
                    return
                continue

        logger.error("All candidate Gemini models failed or exceeded quota limit.")
        yield (
            "Could not connect to Gemini API models. "
            "Please verify your API key and region quota. "
            "Showing retrieved RAG passages directly below."
        )
