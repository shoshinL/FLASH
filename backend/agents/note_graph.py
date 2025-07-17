import math
from typing import Annotated, Dict, TypedDict, List
from langchain.schema.document import Document
import operator
from langchain_core.pydantic_v1 import BaseModel
from langchain_core.vectorstores import VectorStoreRetriever
from langgraph.constants import Send
from langgraph.graph import END, StateGraph
from pydantic import Field
import logging

from .process_pdf import load_pdf, get_retrieval_embeddings, get_question_formulation_chunks
from .retrieval_graph import retrieval_graph
from .note_agents import QuestionGenerator, QuestionsDeduplicator, BasicNoteGenerator, BasicAndReversedNoteGenerator, BasicTypeInAnswerNoteGenerator, ClozeNoteGenerator, ListNoteGenerator
from .retrieval_agents import SingleExpertRouter

logger = logging.getLogger(__name__)

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
    n_questions: The maximum number of questions to generate
    documentpath: The path to the document
    questioning_chunks: The documents to be used for generating questions
    generated_questions: The generated questions
    deduplicated_questions: The deduplicated questions
    questions_with_answers: The questions with answers
    expert_to_route_to: The expert to route to for the index of the q&a pair
    notes: The completed notes
    """
    current_step: str # The current step in the graph used for loading bar
    questioning_context: str # The context of the questioning
    n_questions: int # The maximum number of questions to generate
    documentpath: str # The path to the document
    questioning_chunks: List[Document]
    retriever: Annotated[VectorStoreRetriever, operator.add] # The retriever
    generated_questions: Annotated[List[Dict[str, List[str]]], operator.add] # The generated questions
    deduplicated_questions: Dict[str, List[str]] # The deduplicated questions
    questions_with_answers: Annotated[List[QuestionWithAnswer], operator.add] # The questions with answers
    expert_to_route_to: Annotated[List[str], operator.add] # The expert to route to for the index of the q&a pair
    notes: Annotated[List, operator.add] # The completed notes

class QuestionsState(TypedDict):
    """
    For Question generation map-reduce, if Input File is too large
    
    Attributes:
        n_questions: The maximum number of questions to generate
        questioning_context: The context of the questioning
        quenstioning_chunks: The document to be used for generating questions 
    """
    n_questions: int
    questioning_context: str
    questioning_chunk: List[Document]

class NoteGeneratorState(TypedDict):
    """
    For Note Generation map-reduce.

    Attributes:
        question_with_answer: The question with answer
        notes: The completed notes
    """
    question_with_answer: QuestionWithAnswer
    notes: List

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
    logger.debug("Generating question formulation chunks...")
    questioning_chunks = get_question_formulation_chunks(document, state["questioning_context"])
    logger.debug("Initializing retriever from vector store...")
    retriever = [get_retrieval_embeddings(questioning_chunks)]
    return {
         "current_step": "Generating Questions...",
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
    logger.debug("Generating questions...")
    questions = QuestionGenerator(state["questioning_chunk"], state["n_questions"], state["questioning_context"], [])

    while len(questions["Questions"]) < state["n_questions"]:
        logger.debug(f"Generated {len(questions)} questions, generating more...")
        additional_questions = QuestionGenerator(state["questioning_chunk"], state["n_questions"] - len(questions["Questions"]), state["questioning_context"], questions["Questions"])
        questions["Questions"].extend(additional_questions)

    logger.debug(f"Generated {len(questions['Questions'])} questions.")
    return {"generated_questions": [questions]}

def question_deduplicator(state: NoteGraphState):
    """
    Deduplicates the generated questions.

    Args:
        state (dict): The current state of the graph

    Returns:
        state (dict): The updated state of the graph
    """
    if len(state["questioning_chunks"]) == 1:
        logger.debug("Only one chunk, skipping deduplication.")
        logger.debug("Generating Answers...")
        return {"deduplicated_questions": state["generated_questions"][0], "current_step": "Generating Answers..."}

    logger.debug(f"Deduplicating questions from {len(state['questioning_chunks'])} chunks...")

    try:
        deduplicated_questions = QuestionsDeduplicator(state["generated_questions"], state["n_questions"])
        if type(deduplicated_questions) == list:
            deduplicated_questions = deduplicated_questions[0]
    except Exception as e:
        logger.error(f"Error in question_deduplicator: {e}")

    logger.debug("Generating Answers...")

    return {"deduplicated_questions": deduplicated_questions, "current_step": "Generating Answers..."}

def generate_basic(state: NoteGeneratorState):
    """
    Generates basic notes.

    Args:
        state (dict): The current state of the graph

    Returns:
        state (dict): The updated state of the graph
    """
    notes = BasicNoteGenerator(state["question_with_answer"])
    return {"notes": [notes]}

def generate_basic_and_reversed(state: NoteGeneratorState):
    """
    Generates basic and reversed notes.

    Args:
        state (dict): The current state of the graph

    Returns:
        state (dict): The updated state of the graph
    """
    notes = BasicAndReversedNoteGenerator(state["question_with_answer"])
    return {"notes": [notes]}

def generate_basic_type_in_answer(state: NoteGeneratorState):
    """
    Generates basic type in answer notes.

    Args:
        state (dict): The current state of the graph

    Returns:
        state (dict): The updated state of the graph
    """
    notes = BasicTypeInAnswerNoteGenerator(state["question_with_answer"])
    return {"notes": [notes]}

def generate_cloze(state: NoteGeneratorState):
    """
    Generates cloze notes.

    Args:
        state (dict): The current state of the graph

    Returns:
        state (dict): The updated state of the graph
    """
    notes = ClozeNoteGenerator(state["question_with_answer"])
    return {"notes": [notes]}

def generate_list(state: NoteGeneratorState):
    """
    Generates list notes.

    Args:
        state (dict): The current state of the graph

    Returns:
        state (dict): The updated state of the graph
    """
    notes = ListNoteGenerator(state["question_with_answer"])
    return {"notes": [notes]}

def finish(state: NoteGraphState):
    """
    Finishes the graph.

    Args:
        state (dict): The current state of the graph

    Returns:
        state (dict): The updated state of the graph
    """
    notes = state["notes"]
    documentpath = state["documentpath"]
    return {"current_step": "Finished!", "notes": notes, "documentpath": documentpath}

note_graph = StateGraph(NoteGraphState)
note_graph.add_node("start", lambda state: {"current_step": "Loading Document..."})
note_graph.add_node("document_loader", document_loader)
note_graph.add_node("question_generator", question_generator)
note_graph.add_node("question_deduplicator", question_deduplicator)
note_graph.add_node("answer_generator", retrieval_graph.compile())
note_graph.add_node("generated_answers_state_updater", lambda state: {"current_step": "Generating Cards using Experts..."})
note_graph.add_node("Basic", generate_basic)
note_graph.add_node("BasicAndReversed", generate_basic_and_reversed)
note_graph.add_node("BasicTypeInAnswer", generate_basic_type_in_answer)
note_graph.add_node("Cloze", generate_cloze)
note_graph.add_node("ItemList", generate_list)
note_graph.add_node("finish", finish)


### Edges
def map_questioning_chunks(state: NoteGraphState):
    return [Send("question_generator", {"questioning_chunk": chunk, "n_questions": math.ceil(state["n_questions"] / len(state["questioning_chunks"])), "questioning_context": state["questioning_context"]}) for chunk in state["questioning_chunks"]]

def map_questions(state: NoteGraphState):
    logger.debug("Mapping questions...")
    try:
        logger.debug(f"Questions: {state['deduplicated_questions']['Questions']}")
        logger.debug(f"Retriever: {state['retriever']}")
        logger.debug("Attemtping to map questions...")
        mapper = [Send("answer_generator", {"question": question, "retriever": state["retriever"], }) for question in state["deduplicated_questions"]["Questions"]]
    except Exception as e:
        logger.error(f"Error in map_questions: {e}")

    return mapper

def expert_router(state: NoteGraphState):
    questions_with_answers = state["questions_with_answers"]
    experts_to_route_to = state["expert_to_route_to"]
    logger.debug(f"Routing to experts: {experts_to_route_to}")
    routing = []
    if not experts_to_route_to:
        logger.debug("No experts to route to, finishing...")
        return END
    routing = [Send(experts_to_route_to[i], {"question_with_answer": questions_with_answers}) for i, questions_with_answers in enumerate(questions_with_answers)]
    return routing

note_graph.set_entry_point("start")
note_graph.add_edge("start", "document_loader")
note_graph.add_conditional_edges("document_loader", map_questioning_chunks)
note_graph.add_edge("question_generator", "question_deduplicator")
note_graph.add_conditional_edges("question_deduplicator", map_questions)
note_graph.add_edge("answer_generator", "generated_answers_state_updater")
note_graph.add_conditional_edges("generated_answers_state_updater", expert_router)
note_graph.add_edge("Basic", "finish")
note_graph.add_edge("BasicAndReversed", "finish")
note_graph.add_edge("BasicTypeInAnswer", "finish")
note_graph.add_edge("Cloze", "finish")
note_graph.add_edge("ItemList", "finish")
note_graph.add_edge("finish", END)

graph = note_graph.compile()