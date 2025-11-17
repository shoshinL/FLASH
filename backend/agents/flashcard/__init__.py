"""Flashcard generation agents and models."""

from .agents import (
    Questions,
    QuestionWithAnswer,
    QuestionGenerator,
    QuestionsDeduplicator,
    BasicNoteGenerator,
    BasicAndReversedNoteGenerator,
    BasicTypeInAnswerNoteGenerator,
    ClozeNoteGenerator,
    ListNoteGenerator
)
from .graph import (
    NoteGraphState,
    QuestionsState,
    NoteGeneratorState,
    document_loader,
    question_generator,
    question_deduplicator,
    generate_basic,
    generate_basic_and_reversed,
    generate_basic_type_in_answer,
    generate_cloze,
    generate_list,
    finish,
    map_questioning_chunks,
    map_questions,
    expert_router
)
from .models import (
    BasicModel,
    BasicAndReversedModel,
    BasicTypeInAnswerModel,
    ClozeModel,
    NotePromptModel
)

__all__ = [
    # Agents
    "Questions",
    "QuestionWithAnswer",
    "QuestionGenerator",
    "QuestionsDeduplicator",
    "BasicNoteGenerator",
    "BasicAndReversedNoteGenerator",
    "BasicTypeInAnswerNoteGenerator",
    "ClozeNoteGenerator",
    "ListNoteGenerator",
    # Graph
    "NoteGraphState",
    "QuestionsState",
    "NoteGeneratorState",
    "document_loader",
    "question_generator",
    "question_deduplicator",
    "generate_basic",
    "generate_basic_and_reversed",
    "generate_basic_type_in_answer",
    "generate_cloze",
    "generate_list",
    "finish",
    "map_questioning_chunks",
    "map_questions",
    "expert_router",
    # Models
    "BasicModel",
    "BasicAndReversedModel",
    "BasicTypeInAnswerModel",
    "ClozeModel",
    "NotePromptModel",
]
