#from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser, PydanticOutputParser
from langchain.output_parsers import OutputFixingParser
from pydantic import BaseModel, Field

from .note_models import BasicNote, BasicAndReversedNote, BasicTypeInAnswerNote, ClozeNote, ListNote

from settingUtils.api_key_utils import require_llm

class Score(BaseModel):
    score: str = Field(description="either 'yes' or 'no'")

class Answer(BaseModel):
    answer: str = Field(description="The answer to the question with context and explanation.")

@require_llm
def DocumentGrader(llm, question, documents):
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

@require_llm
def AnswerGenerator(llm, question, documents):
    parser = JsonOutputParser(pydantic_object=Answer)
    prompt = PromptTemplate(
    template="""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
    You are a study assistant that generates an answer to a user question. 
    Use the retrieved documents to answer the question. \n
    If you don't know the answer, just say that you don't know.
    Aim to be as accurate as possible while being brief and concise! \n
    The answer should be a sentence or AT MOST two sentences and should fit well on a flashcard. \n
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

@require_llm
def HallucinationGrader(llm, answer, documents):
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

# Define a simple model for the output
class SingleRouteModel(BaseModel):
        note_type: str = Field(description="The note type: Basic, BasicAndReversed, BasicTypeInAnswer, Cloze, or ItemList")
    
@require_llm
def SingleExpertRouter(llm, question_with_answer):
    parser = PydanticOutputParser(pydantic_object=SingleRouteModel)
    fixing_parser = OutputFixingParser.from_llm(llm=llm, parser=parser, max_retries=1)
    
    prompt = PromptTemplate(
        template="""<system>
You are an expert in routing question-answer pairs to flashcard note types. Your goal is to determine the MOST SUITABLE note type for effective study, not just any type that works.

<critical_instruction>
DO NOT default to "Basic" unless it is truly the best choice. Consider ALL note types carefully before deciding. Each type serves different learning purposes.
</critical_instruction>

<note_types>
<basic>
<when_to_use>{basic_when_to_use}</when_to_use>
<when_not_to_use>{basic_when_not_to_use}</when_not_to_use>
<examples>{basic_examples}</examples>
<counter_examples>{basic_counter_examples}</counter_examples>
</basic>

<basic_and_reversed>
<when_to_use>{basic_and_reversed_when_to_use}</when_to_use>
<when_not_to_use>{basic_and_reversed_when_not_to_use}</when_not_to_use>
<examples>{basic_and_reversed_examples}</examples>
<counter_examples>{basic_and_reversed_counter_examples}</counter_examples>
</basic_and_reversed>

<basic_type_in_answer>
<when_to_use>{basic_type_in_answer_when_to_use}</when_to_use>
<when_not_to_use>{basic_type_in_answer_when_not_to_use}</when_not_to_use>
<examples>{basic_type_in_answer_examples}</examples>
<counter_examples>{basic_type_in_answer_counter_examples}</counter_examples>
</basic_type_in_answer>

<cloze>
<when_to_use>{cloze_when_to_use}</when_to_use>
<when_not_to_use>{cloze_when_not_to_use}</when_not_to_use>
<examples>{cloze_examples}</examples>
<counter_examples>{cloze_counter_examples}</counter_examples>
</cloze>

<item_list>
<when_to_use>{list_when_to_use}</when_to_use>
<when_not_to_use>{list_when_not_to_use}</when_not_to_use>
<examples>{list_examples}</examples>
<counter_examples>{list_counter_examples}</counter_examples>
</item_list>
</note_types>

<evaluation_process>
1. Analyze the question-answer pair structure and content
2. Check if the content involves bidirectional relationships → Consider BasicAndReversed
3. Check if the answer is a specific factual term/date/number → Consider BasicTypeInAnswer  
4. Check if the content has multiple related items or processes → Consider Cloze or ItemList
5. Check if simple Q&A is truly the best approach → Only then consider Basic
6. Select the type that maximizes learning effectiveness for this specific content
</evaluation_process>

<question_answer_pair>
{question_with_answer}
</question_answer_pair>

<task>
Analyze the above question-answer pair and determine the OPTIMAL flashcard type. Consider what would be most effective for a student to learn and retain this information.

Return ONLY the note type name: Basic, BasicAndReversed, BasicTypeInAnswer, Cloze, or ItemList
</task>

{format_instructions}
</system>""",
        input_variables=[
            "question_with_answer", "basic_when_to_use", "basic_when_not_to_use", 
            "basic_examples", "basic_counter_examples", "basic_and_reversed_when_to_use", 
            "basic_and_reversed_when_not_to_use", "basic_and_reversed_examples", 
            "basic_and_reversed_counter_examples", "basic_type_in_answer_when_to_use", 
            "basic_type_in_answer_when_not_to_use", "basic_type_in_answer_examples", 
            "basic_type_in_answer_counter_examples", "cloze_when_to_use", "cloze_when_not_to_use", 
            "cloze_examples", "cloze_counter_examples", "list_when_to_use", 
            "list_when_not_to_use", "list_examples", "list_counter_examples"
        ],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )
    
    chain = prompt | llm | fixing_parser
    
    result = chain.invoke({
        "question_with_answer": question_with_answer, 
        "basic_when_to_use": BasicNote.when_to_use, 
        "basic_when_not_to_use": BasicNote.when_not_to_use, 
        "basic_examples": BasicNote.examples, 
        "basic_counter_examples": BasicNote.counter_examples, 
        "basic_and_reversed_when_to_use": BasicAndReversedNote.when_to_use, 
        "basic_and_reversed_when_not_to_use": BasicAndReversedNote.when_not_to_use, 
        "basic_and_reversed_examples": BasicAndReversedNote.examples, 
        "basic_and_reversed_counter_examples": BasicAndReversedNote.counter_examples, 
        "basic_type_in_answer_when_to_use": BasicTypeInAnswerNote.when_to_use, 
        "basic_type_in_answer_when_not_to_use": BasicTypeInAnswerNote.when_not_to_use, 
        "basic_type_in_answer_examples": BasicTypeInAnswerNote.examples, 
        "basic_type_in_answer_counter_examples": BasicTypeInAnswerNote.counter_examples, 
        "cloze_when_to_use": ClozeNote.when_to_use, 
        "cloze_when_not_to_use": ClozeNote.when_not_to_use, 
        "cloze_examples": ClozeNote.examples, 
        "cloze_counter_examples": ClozeNote.counter_examples, 
        "list_when_to_use": ListNote.when_to_use, 
        "list_when_not_to_use": ListNote.when_not_to_use, 
        "list_examples": ListNote.examples, 
        "list_counter_examples": ListNote.counter_examples
    })
    
    note_type = result.note_type
    return note_type