"""
Prompt Builder for RAG context assembly, prompt formatting, token trimming, and hallucination prevention.
"""
import logging
from app.schemas.chat_schemas import MessageItem

logger = logging.getLogger(__name__)

MAX_CONTEXT_CHARS = 20000  # Approx 5000 tokens (estimating ~4 chars per token)
MAX_MEMORY_MESSAGES = 10   # Last 5 user + 5 assistant messages

SYSTEM_INSTRUCTION = """You are an expert academic research assistant specializing in scientific literature analysis.

STRICT CONSTRAINTS & HALLUCINATION PREVENTION RULES:
1. Answer the user's question ONLY using the supplied retrieved context below.
2. Never invent or fabricate facts, methodologies, experimental results, or mathematical equations.
3. If the answer is unavailable or cannot be logically deduced from the retrieved context below, clearly state: "I couldn't find that information in the uploaded paper."
4. Explain complex concepts, algorithms, and results in simple, clear language without losing academic precision.
5. Whenever possible, explicitly cite the page number(s) from the context where the information originated using the exact format: "[Page X]".
6. Do NOT allow previous conversation memory to override the retrieved document context.
7. Structure your response cleanly using Markdown headings (e.g., `## Executive Summary` or `### Key Findings`), **bold** key terminology, clear bullet points (`- `), and inline citation badges `[Page X]`."""


class PromptBuilder:
    """Combines system instructions, retrieved document chunks, conversation memory, and user questions into a single prompt."""

    @staticmethod
    def _trim_chunks_by_token_limit(retrieved_chunks: list[dict], max_chars: int = MAX_CONTEXT_CHARS) -> list[dict]:
        """Trims lowest-ranked chunks if total character count exceeds token limit (max 5000 tokens / ~20,000 chars).

        Args:
            retrieved_chunks: Chunks sorted by similarity score descending.
            max_chars: Maximum character limit.

        Returns:
            List of chunks fitting within character budget.
        """
        trimmed_chunks = []
        accumulated_chars = 0

        for chunk in retrieved_chunks:
            text = chunk.get("text", "")
            chunk_length = len(text)
            if accumulated_chars + chunk_length <= max_chars:
                trimmed_chunks.append(chunk)
                accumulated_chars += chunk_length
            else:
                logger.warning(
                    f"Trimmed lower-ranked chunk (Page {chunk.get('page')}) to enforce 5000-token context limit."
                )

        return trimmed_chunks

    @staticmethod
    def _format_conversation_history(history: list[MessageItem]) -> str:
        """Formats the last 5 user and 5 assistant messages from history."""
        if not history:
            return ""

        recent_history = history[-MAX_MEMORY_MESSAGES:]
        formatted_pairs = []

        for msg in recent_history:
            role_label = "User" if msg.role.lower() == "user" else "Assistant"
            formatted_pairs.append(f"{role_label}: {msg.content.strip()}")

        return "\n".join(formatted_pairs)

    @classmethod
    def build_prompt(
        cls,
        question: str,
        retrieved_chunks: list[dict],
        history: list[MessageItem] | None = None,
    ) -> str:
        """Builds the complete prompt string to send to Gemini.

        Args:
            question: User question string.
            retrieved_chunks: Top retrieved chunks from FAISS.
            history: Optional list of recent MessageItem objects.

        Returns:
            Formatted prompt string.
        """
        # 1. Trim chunks to fit 5000 token limit
        chunks = cls._trim_chunks_by_token_limit(retrieved_chunks)

        # 2. Format context with explicit page numbers
        if not chunks:
            context_str = "No relevant context was found in the paper."
        else:
            context_blocks = []
            for chunk in chunks:
                page_num = chunk.get("page", "Unknown")
                text = chunk.get("text", "").strip()
                context_blocks.append(f"--- [Page {page_num}] ---\n{text}")
            context_str = "\n\n".join(context_blocks)

        # 3. Format conversation memory
        history_str = cls._format_conversation_history(history or [])

        # 4. Construct final prompt text
        prompt_parts = [
            SYSTEM_INSTRUCTION,
            "\n================ RETRIEVED DOCUMENT CONTEXT ================",
            context_str,
            "============================================================",
        ]

        if history_str:
            prompt_parts.extend([
                "\n================ RECENT CONVERSATION HISTORY ================",
                history_str,
                "============================================================",
            ])

        prompt_parts.extend([
            f"\nUSER QUESTION: {question.strip()}",
            "\nANSWER (Structured Markdown format with headings, bullet points, and [Page X] citations):",
        ])

        final_prompt = "\n".join(prompt_parts)
        logger.info(f"Built prompt (Length: {len(final_prompt)} chars, Included Chunks: {len(chunks)})")
        return final_prompt
