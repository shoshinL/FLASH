"""Agents package - reorganized into flashcard, retrieval, and utils modules.

Backward compatibility exports for old module names:
- note_agents, note_graph, note_models -> flashcard.*
- retrieval_agents, retrieval_graph -> retrieval.*
- parser_utils, process_pdf -> utils.*
"""

# Re-export everything from subdirectories for backward compatibility
from .flashcard import *
from .retrieval import *
from .utils import *

# Create module-level aliases for backward compatibility
from .flashcard import agents as note_agents
from .flashcard import graph as note_graph
from .flashcard import models as note_models
from .retrieval import agents as retrieval_agents
from .retrieval import graph as retrieval_graph
from .utils import parsers as parser_utils
from .utils import pdf as process_pdf

__all__ = [
    # Submodules
    "flashcard",
    "retrieval",
    "utils",
    # Backward compatibility module aliases
    "note_agents",
    "note_graph",
    "note_models",
    "retrieval_agents",
    "retrieval_graph",
    "parser_utils",
    "process_pdf",
]
