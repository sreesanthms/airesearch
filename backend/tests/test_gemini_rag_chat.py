"""
Unit and integration tests for PromptBuilder, GeminiService, and POST /chat SSE streaming endpoint.
"""
import json
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.llm.prompt_builder import PromptBuilder, SYSTEM_INSTRUCTION
from app.llm.gemini_service import GeminiService
from app.schemas.chat_schemas import MessageItem

client = TestClient(app)


def test_prompt_builder_basic():
    """Verify PromptBuilder constructs prompt with system instruction, chunks, and citations."""
    question = "What is the Transformer architecture?"
    chunks = [
        {"page": 1, "text": "We propose the Transformer, an architecture based on attention."},
        {"page": 3, "text": "Scaled Dot-Product Attention is computed as softmax(QK^T / sqrt(d_k))V."},
    ]

    prompt = PromptBuilder.build_prompt(question, chunks)

    assert SYSTEM_INSTRUCTION in prompt
    assert "[Page 1]" in prompt
    assert "[Page 3]" in prompt
    assert "Scaled Dot-Product Attention" in prompt
    assert f"USER QUESTION: {question}" in prompt


def test_prompt_builder_token_trimming():
    """Verify PromptBuilder trims lowest-ranked chunks if context exceeds 20,000 characters."""
    oversized_text = "Word " * 2000  # ~10,000 chars
    chunks = [
        {"page": 1, "text": oversized_text},
        {"page": 2, "text": oversized_text},
        {"page": 3, "text": oversized_text},  # Should be trimmed
    ]

    prompt = PromptBuilder.build_prompt("Test question", chunks)
    assert "[Page 1]" in prompt
    assert "[Page 2]" in prompt
    assert "[Page 3]" not in prompt  # Trimmed due to character limit


def test_prompt_builder_conversation_memory():
    """Verify PromptBuilder formats last 5 user and assistant messages."""
    history = [
        MessageItem(role="user", content="Hello"),
        MessageItem(role="assistant", content="Hi! How can I help?"),
        MessageItem(role="user", content="What is the paper about?"),
        MessageItem(role="assistant", content="It is about deep learning."),
    ]

    prompt = PromptBuilder.build_prompt("Tell me more", [], history=history)
    assert "User: What is the paper about?" in prompt
    assert "Assistant: It is about deep learning." in prompt


def test_chat_missing_paper_404():
    """Verify POST /chat returns 404 if specified paper_id index does not exist."""
    res = client.post(
        "/chat",
        json={"paper_id": "non_existent_paper.pdf", "question": "What is the conclusion?"},
    )
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()


def test_chat_empty_question_400():
    """Verify POST /chat returns 400 for empty questions."""
    res = client.post(
        "/chat",
        json={"paper_id": "some_id", "question": "   "},
    )
    assert res.status_code == 400
    assert "cannot be empty" in res.json()["detail"].lower()
