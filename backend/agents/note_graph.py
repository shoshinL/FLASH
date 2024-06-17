from typing import Annotated, TypedDict, List
from langchain.schema.document import Document
import operator
from langchain_core.pydantic_v1 import BaseModel
from langchain_core.vectorstores import VectorStoreRetriever
from langgraph.constants import Send
from langgraph.graph import END, StateGraph
from pydantic import Field
from .process_pdf import load_pdf, get_retrieval_embeddings, get_question_formulation_chunks
from .retrieval_graph import retrieval_graph
from .note_agents import QuestionGenerator, QuestionsDeduplicator, ExpertRouter, BasicNoteGenerator, BasicAndReversedNoteGenerator, BasicTypeInAnswerNoteGenerator, ClozeNoteGenerator

class Questions(BaseModel):
    Questions: List[str] = Field(description="A List of questions to be asked for studying the key points, terms, definitions, facts, context, and content of the provided document (paper, study notes, lecture slides, ...) very well.")

class QuestionWithAnswer(BaseModel):
    Question: str = Field(description="A Question to be asked for studying the key points, terms, definitions, facts, context, and content of a document (paper, study notes, lecture slides, ...) very well.")
    Answer: str = Field(description="The answer to the question with context and explanation.")

class NoteGraphState(TypedDict):
    """
    Represents the state of the graph at a given time.

    Attributes:
    current_step: The current step in the graph used for loading bar
    questioning_context: The context of the questioning
    documentpath: The path to the document
    questioning_chunks: The documents to be used for generating questions
    generated_questions: The generated questions
    deduplicated_questions: The deduplicated questions
    questions_with_answers: The questions with answers
    notes: The completed notes
    """
    current_step: str # The current step in the graph used for loading bar
    questioning_context: str # The context of the questioning
    documentpath: str # The path to the document
    questioning_chunks: List[Document]
    retriever: VectorStoreRetriever
    generated_questions: Annotated[Questions, operator.add] # The generated questions
    deduplicated_questions: Questions
    questions_with_answers: Annotated[List[QuestionWithAnswer], operator.add] # The questions with answers
    notes: Annotated[List[BaseModel], operator.add] # The completed notes

class QuestionsState(TypedDict):
    """
    For Question generation map-reduce, if Input File is too large
    
    Attributes:
        questioning_context: The context of the questioning
        quenstioning_chunks: The document to be used for generating questions 
    """
    questioning_context: str
    questioning_chunks: List[Document]

### Nodes
def document_loader(state: NoteGraphState):
    """
   Loads the document from the provided file path.
   Generates the document chunks for the questioning
   and embeds the document chunks for the retrieval.

   Args:
        state (dict): The current state of the graph

   Returns:
        state (dict): The updated state of the graphall
    """
    document = load_pdf(state["documentpath"])
    questioning_chunks = get_question_formulation_chunks(document)
    retriever = get_retrieval_embeddings(questioning_chunks)
    return {
         "current_step": "Starting Question Generation...",
         "questioning_chunks": questioning_chunks,
         "retriever": retriever
    }

def question_generator(state: QuestionsState):
    """
    Generates questions from the provided document.

    Args:
        state (dict): The current state of the graph

    Returns:
        state (dict): The updated state of the graph
    """
    questions = QuestionGenerator(state["questioning_chunks"], state["questioning_context"])
    return {"generated_questions": [questions]}

def question_deduplicator(state: NoteGraphState):
    """
    Deduplicates the generated questions.

    Args:
        state (dict): The current state of the graph

    Returns:
        state (dict): The updated state of the graph
    """
    deduplicated_questions = QuestionsDeduplicator(state["generated_questions"])

    return {"deduplicated_questions": [deduplicated_questions], "current_step": "Starting Card Generation..."}

def generate_basic(state: NoteGraphState):
    """
    Generates basic notes.

    Args:
        state (dict): The current state of the graph

    Returns:
        state (dict): The updated state of the graph
    """
    notes = BasicNoteGenerator(state["questions_with_answers"])
    return {"notes": notes}

def generate_basic_and_reversed(state: NoteGraphState):
    """
    Generates basic and reversed notes.

    Args:
        state (dict): The current state of the graph

    Returns:
        state (dict): The updated state of the graph
    """
    notes = BasicAndReversedNoteGenerator(state["questions_with_answers"])
    return {"notes": notes}

def generate_basic_type_in_answer(state: NoteGraphState):
    """
    Generates basic type in answer notes.

    Args:
        state (dict): The current state of the graph

    Returns:
        state (dict): The updated state of the graph
    """
    notes = BasicTypeInAnswerNoteGenerator(state["questions_with_answers"])
    return {"notes": notes}

def generate_cloze(state: NoteGraphState):
    """
    Generates cloze notes.

    Args:
        state (dict): The current state of the graph

    Returns:
        state (dict): The updated state of the graph
    """
    notes = ClozeNoteGenerator(state["questions_with_answers"])
    return {"notes": notes}

note_graph = StateGraph(NoteGraphState)
note_graph.add_node("document_loader", document_loader)
note_graph.add_node("question_generator", question_generator)
note_graph.add_node("question_deduplicator", question_deduplicator)
note_graph.add_node("answer_generator", retrieval_graph.compile())
note_graph.add_node("Basic", generate_basic)
note_graph.add_node("BasicAndReversed", generate_basic_and_reversed)
note_graph.add_node("BasicTypeInAnswer", generate_basic_type_in_answer)
note_graph.add_node("Cloze", generate_cloze)


### Edges
def map_questioning_chunks(state: NoteGraphState):
    return [Send("question_generator", {"document": doc}) for doc in state["questioning_chunks"]]

def map_questions(state: NoteGraphState):
    return [Send("answer_generator", {"question": question}) for question in state["deduplicated_questions"]]

def expert_router(state: NoteGraphState):
    questions_with_answers = state["questions_with_answers"]
    expert = ExpertRouter(questions_with_answers)
    routing = []
    for key in expert.keys():
        indices = expert[key]
        questions_with_answers_for_key = [questions_with_answers[i] for i in indices]
        routing.append(Send(key, {"questions_with_answer": questions_with_answers_for_key}))
    return routing

note_graph.set_entry_point("document_loader")
note_graph.add_conditional_edges("document_loader", map_questioning_chunks)
note_graph.add_edge("question_generator", "question_deduplicator")
note_graph.add_conditional_edges("question_deduplicator", map_questions)
note_graph.add_conditional_edges("answer_generator", expert_router)
note_graph.add_edge("Basic", END)
note_graph.add_edge("BasicAndReversed", END)
note_graph.add_edge("BasicTypeInAnswer", END)
note_graph.add_edge("Cloze", END)

graph = note_graph.compile()
from IPython.display import Image, display

# Setting xray to 1 will show the internal structure of the nested graph
display(Image(graph.get_graph(xray=1).draw_mermaid_png()))