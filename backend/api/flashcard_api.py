"""
Flashcard Generation API

Handles flashcard generation and saving to Anki decks.
"""

import json
import os
import logging
import webview
from .base import BaseAPI
from agents.flashcard.graph import graph

logger = logging.getLogger(__name__)


class FlashcardAPI(BaseAPI):
    """API endpoints for flashcard generation and management."""

    def generate_flashcards(self, content, file_path, card_amount):
        """
        Generate flashcards from content using the flashcard agent.

        Args:
            content: Text content to generate flashcards from
            file_path: Path to the source document
            card_amount: Number of flashcards to generate

        Returns:
            Completion message
        """
        last_step = ""
        progress = 0

        for state in graph.stream({"questioning_context": content, "documentpath": file_path, "n_questions": card_amount}):
            key = next(iter(state))
            try:
                current_step = state[key]["current_step"]
            except:
                continue

            if current_step != last_step:
                logger.debug(f"Current step in graph: {current_step}")
                last_step = current_step
                progress += 20
                update = {"progress": progress, "message": current_step}
                if current_step == "Finished!":
                    flashcards = state[key]["notes"]
                    filename = os.path.basename(state[key]["documentpath"])
                    update = {
                        "progress": 100,
                        "message": "Complete!",
                        "result": {"flashcards": flashcards, "filename": filename}
                    }
                webview.windows[0].evaluate_js(f"window.dispatchEvent(new CustomEvent('backendUpdate', {{detail: {json.dumps(update)}}}));")

        return "Flashcard generation completed"

    def save_accepted_flashcards(self, flashcards, filename):
        """
        Save accepted flashcards to the selected Anki deck.

        Args:
            flashcards: List of flashcard dictionaries
            filename: Source filename for the flashcards

        Returns:
            Success or error message
        """
        if not flashcards:
            return "ERROR"
        try:
            self.settings_manager.add_generated_cards_to_deck(filename, flashcards)
            return "Success!!"
        except Exception as e:
            logger.error(f"Error saving flashcards: {e}")
            return "ERROR"
