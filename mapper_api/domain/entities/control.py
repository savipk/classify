"""Domain entity for Control. Framework-free. Holds textual description and optional external id.

Implements: Control(text: str, id: Optional[str])
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True, slots=True)
class Control:
    """Represents a control record to be mapped.

    Attributes:
        text: The control description text to analyze.
        id: Optional external identifier.
    """
    text: str
    id: Optional[str] = None

    # Class constants for validation
    MIN_LENGTH = 50

    def ensure_not_empty(self) -> None:
        """Ensure control description is not empty or whitespace-only."""
        if not self.text or not self.text.strip():
            raise ValueError("control description must not be empty")

    def ensure_minimum_length(self) -> None:
        """Ensure control description meets minimum length requirement."""
        stripped_text = self.text.strip()
        if len(stripped_text) < self.MIN_LENGTH:
            raise ValueError(
                f"control description must be at least {self.MIN_LENGTH} characters long, "
                f"got {len(stripped_text)}"
            )

    def ensure_is_english(self) -> None:
        """Ensure control description is in English using langdetect."""
        try:
            from langdetect import detect, LangDetectException
        except ImportError:
            # Fallback if langdetect is not available
            raise ValueError("Language detection library not available")

        text = self.text.strip()
        if not text:
            return  # Empty check handled elsewhere

        try:
            detected_language = detect(text)
            if detected_language != 'en':
                raise ValueError(
                    f"control description must be in English, detected language: {detected_language}"
                )
        except LangDetectException:
            # If detection fails (too short text, etc.), we'll be lenient
            # and only check for obvious non-English patterns
            import re
            non_english_patterns = [
                r'[\u4e00-\u9fff]',  # Chinese
                r'[\u0400-\u04ff]',  # Cyrillic
                r'[\u0600-\u06ff]',  # Arabic
                r'[\u3040-\u309f]',  # Hiragana
                r'[\u30a0-\u30ff]',  # Katakana
            ]
            
            for pattern in non_english_patterns:
                if re.search(pattern, text):
                    raise ValueError("control description must be in English")

    def validate_all(self) -> None:
        """Run all control validations."""
        self.ensure_not_empty()
        self.ensure_minimum_length()
        self.ensure_is_english()
