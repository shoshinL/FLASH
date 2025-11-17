import os
import webview
import logging
import sys
from anki.errors import DBError

from settings.settings_manager import SettingsManager
from settings.settings_context import SettingsContext
from ui.alerts import custom_alert, check_settings
from api import AnkiAPI, ProviderAPI, EmbeddingAPI, ThinkingAPI, FlashcardAPI

# Configure logging to show only our app's debug messages, not external libraries
logging.basicConfig(level=logging.INFO,  # Set root logger to INFO
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler(sys.stdout)])

# Set our application modules to DEBUG level
logging.getLogger('settings').setLevel(logging.DEBUG)
logging.getLogger('agents').setLevel(logging.DEBUG)
logging.getLogger('anki').setLevel(logging.DEBUG)
logging.getLogger(__name__).setLevel(logging.DEBUG)

# Silence noisy external libraries
logging.getLogger('httpcore').setLevel(logging.WARNING)
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('requests').setLevel(logging.WARNING)
logging.getLogger('ollama').setLevel(logging.WARNING)
logging.getLogger('langchain').setLevel(logging.WARNING)
logging.getLogger('chromadb').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


class Api:
    """Main API class that delegates to specialized API modules."""

    def __init__(self):
        # Initialize specialized API modules (private to prevent webview introspection)
        self._anki_api = AnkiAPI()
        self._provider_api = ProviderAPI()
        self._embedding_api = EmbeddingAPI()
        self._thinking_api = ThinkingAPI()
        self._flashcard_api = FlashcardAPI()
    # ========== Window-specific utility methods ==========

    def show_alert(self, message):
        """Show an alert message to the user."""
        webview.windows[0].evaluate_js(custom_alert([message], 7000))

    def valid_settings(self):
        """Check if all required settings are configured."""
        return check_settings(webview.windows[0])

    def select_file(self):
        """Open file dialog to select a PDF file."""
        file_types = ('PDF Files (*.pdf)',)
        result = webview.windows[0].create_file_dialog(webview.OPEN_DIALOG, file_types=file_types, allow_multiple=False)
        if result:
            return result[0]
        return None

    # ========== Flashcard API Endpoints (delegate to FlashcardAPI) ==========

    def generate_flashcards(self, content, file_path, card_amount):
        """Generate flashcards from content."""
        return self._flashcard_api.generate_flashcards(content, file_path, card_amount)

    def save_accepted_flashcards(self, flashcards, filename):
        """Save accepted flashcards to Anki deck."""
        return self._flashcard_api.save_accepted_flashcards(flashcards, filename)

    # ========== Anki API Endpoints (delegate to AnkiAPI) ==========

    def get_settings(self):
        """Get all application settings."""
        return self._anki_api.get_settings()

    def get_profiles(self, anki_db_path):
        """Get all available Anki profiles."""
        return self._anki_api.get_profiles(anki_db_path)

    def get_decks(self, profile):
        """Get all decks for a profile."""
        return self._anki_api.get_decks(profile)

    def get_selected_deck(self):
        """Get currently selected deck."""
        return self._anki_api.get_selected_deck()

    def get_selected_profile(self):
        """Get currently selected profile."""
        return self._anki_api.get_selected_profile()

    def select_file_path(self):
        """Select Anki database file."""
        return self._anki_api.select_file_path()

    def set_profile(self, profile):
        """Set active Anki profile."""
        return self._anki_api.set_profile(profile)

    def set_deck(self, deck_name):
        """Set active deck."""
        return self._anki_api.set_deck(deck_name)

    # ========== Provider API Endpoints (delegate to ProviderAPI) ==========

    def get_available_providers(self):
        """Get list of all available LLM providers."""
        return self._provider_api.get_available_providers()

    def get_provider_config(self):
        """Get current provider configuration."""
        return self._provider_api.get_provider_config()

    def get_available_models(self, provider):
        """Get available models for a specific provider."""
        return self._provider_api.get_available_models(provider)

    def set_provider_api_key(self, provider, api_key):
        """Set API key for a specific provider."""
        return self._provider_api.set_provider_api_key(provider, api_key)

    def delete_provider_api_key(self, provider):
        """Delete API key for a specific provider."""
        return self._provider_api.delete_provider_api_key(provider)

    def get_provider_api_keys_status(self):
        """Get status of which providers have API keys set."""
        return self._provider_api.get_provider_api_keys_status()

    def set_provider_config(self, provider, model=None):
        """Set the current provider and model."""
        return self._provider_api.set_provider_config(provider, model)

    def validate_provider(self, provider, api_key=None, model=None):
        """Validate a provider configuration."""
        return self._provider_api.validate_provider(provider, api_key, model)

    def set_api_key(self, api_key):
        """Legacy method: Set API key for OpenAI."""
        return self._provider_api.set_api_key(api_key)

    # ========== Embedding API Endpoints (delegate to EmbeddingAPI) ==========

    def get_embedding_providers(self):
        """Get list of providers that support embeddings."""
        return self._embedding_api.get_embedding_providers()

    def get_embedding_config(self):
        """Get current embedding configuration."""
        return self._embedding_api.get_embedding_config()

    def get_available_embedding_models(self, provider):
        """Get available embedding models for a specific provider."""
        return self._embedding_api.get_available_embedding_models(provider)

    def set_embedding_config(self, provider, model=None):
        """Set the embedding provider and model."""
        return self._embedding_api.set_embedding_config(provider, model)

    # ========== Thinking API Endpoints (delegate to ThinkingAPI) ==========

    def get_thinking_config(self):
        """Get thinking/reasoning configuration."""
        return self._thinking_api.get_thinking_config()

    def set_thinking_config(self, config):
        """Set thinking/reasoning configuration."""
        return self._thinking_api.set_thinking_config(config)

    def check_thinking_support(self, provider, model):
        """Check if a provider/model supports thinking/reasoning."""
        return self._thinking_api.check_thinking_support(provider, model)


def get_entrypoint():
    def exists(path):
        return os.path.exists(os.path.join(os.path.dirname(__file__), path))

    if exists("../gui/index.html"):  # unfrozen development
        return "../gui/index.html"
    if exists("../Resources/gui/index.html"):  # frozen py2app
        return "../Resources/gui/index.html"
    if exists("./gui/index.html"):
        return "./gui/index.html"
    raise Exception("No index.html found")

entry = get_entrypoint()

def anki_close_dialog(window):
    window.create_confirmation_dialog('NOTICE', f'Please close Anki before restarting FLASH!')
    window.destroy()
    exit(1)

if __name__ == "__main__":
    logging.debug("Starting application")
    api = Api()
    window = webview.create_window("FLASH", entry, maximized=True, js_api=api)

    try:
        logging.debug("Initializing SettingsManager")
        settings_manager = SettingsManager()
        SettingsContext.set_settings_manager(settings_manager)
        logging.debug("SettingsManager initialized successfully")
        window.events.loaded += lambda: check_settings(window)
        logging.debug("Starting webview")
        webview.start()
    except DBError as e:
        logging.error(f"DBError occurred: {str(e)}")
        webview.start(anki_close_dialog, window)
    except Exception as e:
        logging.error(f"Unexpected error occurred: {str(e)}")

    