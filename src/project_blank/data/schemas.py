"""Core data schemas for training examples.

These Pydantic models are the canonical representation of data records
throughout the pipeline. Every JSONL entry, every generated example,
and every training sample passes through these schemas.

Tier system (answer-only token budgets)::

    short:   ≤180 tokens  — 1-2 sentences, direct answer
    medium:  ≤400 tokens  — 3-5 sentences, balanced explanation
    long:    ≤650 tokens  — 1-2 paragraphs with examples
    list:    ≤450 tokens  — numbered/bulleted items
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class Tier(StrEnum):
    """Answer length tier with associated token budget."""

    SHORT = "short"
    MEDIUM = "medium"
    LONG = "long"
    LIST = "list"

    @property
    def max_tokens(self) -> int:
        """Token budget for this tier (answer content only)."""
        return _TIER_BUDGETS[self]

    @property
    def label_tr(self) -> str:
        """Turkish display label."""
        return _TIER_LABELS_TR[self]


_TIER_BUDGETS: dict[Tier, int] = {
    Tier.SHORT: 180,
    Tier.MEDIUM: 400,
    Tier.LONG: 650,
    Tier.LIST: 450,
}

_TIER_LABELS_TR: dict[Tier, str] = {
    Tier.SHORT: "KISA",
    Tier.MEDIUM: "NORMAL",
    Tier.LONG: "DETAYLI",
    Tier.LIST: "LİSTE",
}


class Message(BaseModel):
    """A single message in a conversation."""

    role: str = Field(description="One of: system, user, assistant")
    content: str = Field(min_length=1, description="Message content, must not be empty")


class TrainingExample(BaseModel):
    """A complete training example with metadata.

    The ``messages`` field follows the Mistral v0.3 chat format:
    [system, user, assistant] with alternating user/assistant turns.
    """

    messages: list[Message] = Field(min_length=2)
    tier: Tier = Field(description="Answer length tier")
    source: str = Field(
        default="generated",
        description="Origin: 'seed', 'generated', 'curated', 'migrated'",
    )
    domain: str = Field(
        default="general_educational",
        description="Domain: 'general_educational', 'law_study', etc.",
    )
    question_hash: str = Field(
        default="",
        description="MD5 of normalized question for dedup",
    )
    metadata: dict = Field(
        default_factory=dict,
        description="Arbitrary metadata: provider, model, latency, etc.",
    )

    @property
    def question(self) -> str:
        """Extract user question from messages."""
        for msg in self.messages:
            if msg.role == "user":
                return msg.content
        return ""

    @property
    def answer(self) -> str:
        """Extract assistant answer from messages."""
        for msg in self.messages:
            if msg.role == "assistant":
                return msg.content
        return ""
