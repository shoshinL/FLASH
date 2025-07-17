from typing import TypedDict, List
from langchain.schema.document import Document
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_core.pydantic_v1 import BaseModel
from langgraph.graph import END, StateGraph
from pydantic import Field
import logging
from .retrieval_agents import DocumentGrader, AnswerGenerator, HallucinationGrader, SingleExpertRouter

logger = logging.getLogger(__name__)

class Question(BaseModel):
    Question: str = Field(description="A Question to be asked for studying the key points, terms, definitions, facts, context, and content of a document (paper, study notes, lecture slides, ...) very well.")

class QuestionWithAnswer(BaseModel):
    Question: str = Field(description="A Question to be asked for studying the key points, terms, definitions, facts, context, and content of a document (paper, study notes, lecture slides, ...) very well.")
    Answer: str = Field(description="The answer to the question with context and explanation.")

## Create Embeddings here
class RetrievalGraphState(TypedDict):
    """
    Represents the state of the graph at a given time.

    Attributes: 
        question (str): The question to be answered.
        questions_with_answers (List[QuestionWithAnswer]): The questions with answers.
        expert_to_route_to (List[str]): The expert to route to for the index of the q&a pair.
        retriever (List[VectorStoreRetriever]): The retriever to use for retrieving documents.
        documents (List[Document]): The documents retrieved.
        hallucinated (bool): Whether the answer is hallucinated or not.
    """
    question: str
    questions_with_answers: List[QuestionWithAnswer] # Add only the given question with answer as a single-element list
    expert_to_route_to: List[str] # The expert to route to for the index of the q&a pair
    retriever: List[VectorStoreRetriever]
    documents: List[Document]
    hallucinated: bool

### Nodes
def retrieve(state):
    """
    Retrieve documents from vectorstore

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, documents, that contains retrieved documents
    """
    question = state["question"]

    logger.debug(f"Retrieving documents for question {question}...")
    # Retrieval
    try:
        documents = state["retriever"][0].invoke(question)
    except Exception as e:
        logger.error(f"Error in retrieving documents: {e}")
        documents = []
    return {"documents": documents, "question": question, "questions_with_answers": []}

def grade_documents(state):
    """
    Filters out irrelevant documents

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): The state with only relevant documents
    """
    logger.debug(f"Grading documents for question {state['question']}...")
    question = state["question"]
    documents = state["documents"]
    filtered_documents = []
    for document in documents:
        score = DocumentGrader(question, document)
        grade = score["score"]
        if grade.lower() == "yes":
            filtered_documents.append(document)
    logger.debug("DONE GRADING")

    return {"documents": filtered_documents, "question": question}


def generate_answers(state):
    """
    Generate answers for the given question

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): The state with the answers added to the questions
    """
    logger.debug(f"Generating answer for question {state['question']}...")
    question = state["question"]
    documents = state["documents"]
    hallucinated = (state["questions_with_answers"] != [])

    answer = AnswerGenerator(question, documents)
    logger.debug("DONE GENERATING ANSWER")
    return {"questions_with_answers": [{"Question": question, "Answer": answer['answer']}], "hallucinated": hallucinated, "retriever": []}

def answer_scrubber(state):
    """
    Scrub the answers

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): The state with the scrubbed answers
    """

    return {"questions_with_answers": [], "retriever": []}

def route_to_expert(state):
    """
    Assigns expert ot route to based on the question

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): The state with the expert to route to
    """
    question_with_answer = state["questions_with_answers"][0]
    logger.debug(f"Routing to expert for question {question_with_answer['Question']}...")
    expert = SingleExpertRouter(question_with_answer)
    logger.debug(f"Assigned expert: {expert} for question {question_with_answer['Question']}")
    return {"expert_to_route_to": [expert]}
    
retrieval_graph = StateGraph(RetrievalGraphState)
retrieval_graph.add_node("retrieve", retrieve)
retrieval_graph.add_node("grade_documents", grade_documents)
retrieval_graph.add_node("generate_answers", generate_answers)
retrieval_graph.add_node("answer_scrubber", answer_scrubber)
retrieval_graph.add_node("route_to_expert", route_to_expert)

### Edges
def check_if_documents_left(state):
    """
    Check if there are any documents left

    Args:
        state (dict): The current graph state

    Returns:
        str: The next node to go to
    """

    if len(state["documents"]) == 0:
        return END
    return "generate_answers"

def grade_hallucination(state):
    """
    Grade the generation of answers

    Args:
        state (dict): The current graph state

    Returns:
        str: The next node to go to
    """
    documents = state["documents"]
    answer = state["questions_with_answers"][0]["Answer"]

    grade = HallucinationGrader(answer, documents)
    grade = grade["score"]
    if grade.lower() == "no":
        if state["hallucinated"]:
            return "answer_scrubber"
        return "generate_answers"
    return "route_to_expert"

retrieval_graph.set_entry_point("retrieve")
retrieval_graph.add_edge("retrieve", "grade_documents")
retrieval_graph.add_conditional_edges("grade_documents", check_if_documents_left)
retrieval_graph.add_conditional_edges("generate_answers", grade_hallucination)
retrieval_graph.set_finish_point("answer_scrubber")
retrieval_graph.set_finish_point("route_to_expert")
