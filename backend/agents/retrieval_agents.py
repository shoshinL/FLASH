from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from apiUtils.key_manager import get_api_key

class Score(BaseModel):
    score: str = Field(description="either 'yes' or 'no'")

class Answer(BaseModel):
    answer: str = Field(description="The answer to the question with context and explanation.")

model_id = "meta/llama3-70b-instruct"
api_key = get_api_key()
llm = ChatNVIDIA(model=model_id, nvidia_api_key=api_key, temperature=0)

def DocumentGrader(question, documents):
    parser = JsonOutputParser(pydantic_object=Score)
    prompt = PromptTemplate(
    template="""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
    You are a grader assessing relevance
    of a retrieved document to a user question. If the document contains keywords related to the user question,
    grade it as relevant. It does not need to be a stringent test. The goal is to filter out erroneous retrievals. \n
    Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question. \n
    Provide the binary score as a JSON with a single key 'score' and no premable or explanation.You are a document grader.\n
    Here is the retrieved document: \n\n {document} \n\n
    Here is the user question: {question} \n \n
    {format_instructions}
    <|eot_id|><|start_header_id|>assistant<|end_header_id|>
    """,
    input_variables=["question", "document"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
    )
    chain = prompt | llm | parser
    return (chain.invoke({"question": question, "document": documents}))

def AnswerGenerator(question, documents):
    parser = JsonOutputParser(pydantic_object=Answer)
    prompt = PromptTemplate(
    template="""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
    You are a study assistant that generates an answer to a user question. 
    Use the retrieved documents to answer the question. \n
    If you don't know the answer, just say that you don't know.
    Aim to be as accurate as possible and provide a detailed answer to help the user understand the topic better. \n
    Here is the user question: {question} \n
    Here are the retrieved documents: \n\n {documents} \n\n
    {format_instructions}
    <|eot_id|><|start_header_id|>assistant<|end_header_id|>
    """,
    input_variables=["question", "documents"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
    )
    chain = prompt | llm | parser
    return (chain.invoke({"question": question, "documents": documents}))

    
def HallucinationGrader(answer, documents):
    parser = JsonOutputParser(pydantic_object=Score)
    prompt = PromptTemplate(
    template=""" <|begin_of_text|><|start_header_id|>system<|end_header_id|>
    You are a grader assessing whether an answer is grounded in / supported by a set of facts.
    Give a binary 'yes' or 'no' score to indicate whether the answer is grounded in / supported by a set of facts. \n
    'yes' if the answer is grounded in / supported by the facts, 'no' if it is not. \n
    Provide the binary score as a JSON with a single key 'score' and no preamble or explanation. \n
    Here are the facts:
    \n ------- \n
    {documents}
    \n ------- \n
    Here is the answer: {answer} \n
    {format_instructions}
    <|eot_id|><|start_header_id|>assistant<|end_header_id|>
    """,
    input_variables=["answer", "documents"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
    )
    chain = prompt | llm | parser
    return (chain.invoke({"answer": answer, "documents": documents}))