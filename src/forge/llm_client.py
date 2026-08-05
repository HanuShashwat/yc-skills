"""
Unified LLM Client with Provider Rotation.
"""

import json
import logging
import os
import sqlite3
import time
from datetime import datetime, timezone
from typing import Dict, Tuple, Union

import openai

from src.config import load_config, ProviderConfig

logger = logging.getLogger(__name__)


class LLMClient:
    """Client for LLM interactions with provider rotation and quota tracking."""

    def __init__(self, db_path: str = "data/registry.db"):
        self.config = load_config()
        self.db_path = db_path
        # Ensure errors directory exists
        os.makedirs("data/errors", exist_ok=True)

    def _get_today_usage(self, provider_name: str) -> int:
        """Get the total tokens used by a provider today."""
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT SUM(total_tokens) FROM usage_log WHERE provider = ? AND timestamp LIKE ?",
                    (provider_name, f"{today}%"),
                )
                result = cursor.fetchone()
                return result[0] if result and result[0] else 0
        except sqlite3.Error as e:
            logger.error("Failed to query usage log for %s: %s", provider_name, e)
            return 0

    def get_provider(self, estimated_tokens: int = 0) -> Tuple[str, ProviderConfig]:
        """Get the best available provider based on quota and priority."""
        buffer_percent = self.config.providers.quotas.buffer_percent
        buffer_multiplier = (100 - buffer_percent) / 100.0

        candidates = []
        for name, provider in self.config.providers.providers.items():
            used = self._get_today_usage(name)
            limit = provider.daily_token_limit
            remaining = (limit * buffer_multiplier) - used

            if remaining >= estimated_tokens:
                candidates.append((name, provider, remaining))

        if not candidates:
            raise RuntimeError("All providers exhausted or insufficient quota.")

        # Sort by priority (lower is better), then by remaining quota (descending)
        candidates.sort(key=lambda x: (x[1].priority, -x[2]))

        best_name, best_provider, _ = candidates[0]
        return best_name, best_provider

    def _log_usage(
        self,
        provider: str,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        call_type: str,
        success: bool,
        error_message: str | None = None,
        batch_id: str | None = None,
    ):
        """Log the usage of an LLM call to the database."""
        total = prompt_tokens + completion_tokens
        timestamp = datetime.now(timezone.utc).isoformat()
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO usage_log (
                        provider, model, batch_id, prompt_tokens, completion_tokens, total_tokens, 
                        cost_estimate_usd, call_type, timestamp, success, error_message
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        provider,
                        model,
                        batch_id,
                        prompt_tokens,
                        completion_tokens,
                        total,
                        0.0,
                        call_type,
                        timestamp,
                        1 if success else 0,
                        error_message,
                    ),
                )
                conn.commit()
        except sqlite3.Error as e:
            logger.error("Failed to log usage: %s", e)

    def _save_error(self, batch_id: str | None, error_content: str):
        """Save raw error responses to a file for review."""
        safe_batch_id = batch_id or "unknown"
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        path = f"data/errors/{safe_batch_id}_{timestamp}.json"
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(error_content)
        except OSError as e:
            logger.error("Failed to save error output: %s", e)

    def call(
        self,
        prompt: str,
        call_type: str,
        temperature: float = 0.3,
        response_format_json: bool = True,
        batch_id: str | None = None,
        estimated_tokens: int = 1000,
    ) -> Union[str, Dict]:
        """
        Call the LLM with the best available provider.

        Handles retries, JSON extraction fallback, and usage logging.
        """
        provider_name, provider = self.get_provider(estimated_tokens)

        client = openai.OpenAI(
            api_key=provider.api_key,
            base_url=provider.base_url,
            timeout=provider.timeout,
        )

        max_retries = provider.max_retries
        attempt = 0
        json_retries_remaining = 1
        current_temp = temperature

        while attempt <= max_retries:
            attempt += 1
            try:
                kwargs = {
                    "model": provider.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": current_temp,
                }

                if response_format_json:
                    kwargs["response_format"] = {"type": "json_object"}

                try:
                    response = client.chat.completions.create(**kwargs)
                except openai.BadRequestError as e:
                    # Fall back to prompt-based JSON extraction if provider doesn't support json_object
                    if response_format_json and "response_format" in str(e):
                        logger.warning(
                            "Provider %s does not support JSON response format. Falling back.",
                            provider_name,
                        )
                        del kwargs["response_format"]
                        response = client.chat.completions.create(**kwargs)
                    else:
                        raise

                content = response.choices[0].message.content
                usage = response.usage
                prompt_tokens = usage.prompt_tokens if usage else 0
                completion_tokens = usage.completion_tokens if usage else 0

                self._log_usage(
                    provider=provider_name,
                    model=provider.model,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    call_type=call_type,
                    success=True,
                    batch_id=batch_id,
                )

                if response_format_json:
                    try:
                        return json.loads(content)
                    except json.JSONDecodeError as e:
                        self._save_error(batch_id, content)
                        if json_retries_remaining > 0:
                            logger.warning(
                                "JSON parse failed, retrying once with temperature=0.1. Error: %s",
                                e,
                            )
                            json_retries_remaining -= 1
                            current_temp = 0.1
                            continue
                        else:
                            raise RuntimeError(f"Failed to parse JSON from LLM: {e}")
                else:
                    return content

            except (
                openai.RateLimitError,
                openai.APITimeoutError,
                openai.APIConnectionError,
            ) as e:
                self._log_usage(
                    provider_name,
                    provider.model,
                    0,
                    0,
                    call_type,
                    False,
                    str(e),
                    batch_id,
                )
                if attempt > max_retries:
                    raise RuntimeError(
                        f"Exhausted retries ({max_retries}) for provider {provider_name}. Last error: {e}"
                    )

                logger.warning(
                    "Transient error on %s, retrying (%d/%d)...",
                    provider_name,
                    attempt,
                    max_retries,
                )
                time.sleep(2**attempt)
            except Exception as e:
                self._log_usage(
                    provider_name,
                    provider.model,
                    0,
                    0,
                    call_type,
                    False,
                    str(e),
                    batch_id,
                )
                raise
