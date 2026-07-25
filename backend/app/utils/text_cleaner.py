"""
Utility module for cleaning and formatting extracted text.
"""
import re


class TextCleaner:
    """Provides methods for cleaning raw PDF text while preserving structure."""

    @staticmethod
    def clean_text(raw_text: str) -> str:
        """Cleans extracted text by removing repeated blank lines and extra whitespace.

        Args:
            raw_text: Raw text string extracted from PDF.

        Returns:
            Cleaned and normalized text string with preserved paragraph boundaries.
        """
        if not raw_text:
            return ""

        # Normalize line endings
        text = raw_text.replace("\r\n", "\n").replace("\r", "\n")

        # Trim spaces at the end of each line
        lines = [line.rstrip() for line in text.split("\n")]
        text = "\n".join(lines)

        # Replace 3 or more consecutive newlines with exactly 2 newlines (preserve paragraphs)
        text = re.sub(r"\n{3,}", "\n\n", text)

        # Replace non-breaking spaces and tabs with standard space
        text = text.replace("\xa0", " ").replace("\t", " ")

        # Replace multiple horizontal spaces within lines with a single space
        text = re.sub(r"[ ]{2,}", " ", text)

        return text.strip()
