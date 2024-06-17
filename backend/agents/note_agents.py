from typing import List
from ankiUtils.note_models import NoteModel, BasicModel, BasicAndReversedModel, BasicTypeInAnswerModel, ClozeModel, BasicModel, BasicAndReversedModel, BasicTypeInAnswerModel, ClozeModel
from .note_graph import Questions, QuestionWithAnswer

from langchain.output_parsers import PydanticOutputParser, JsonOutputParser
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field
from apiUtils.key_manager import get_api_key

model_id = "meta/llama3-70b-instruct"
api_key = get_api_key()
llm = ChatNVIDIA(model=model_id, nvidia_api_key=api_key, temperature=0)

BasicNote = NoteModel(
    type="Basic",
    model=BasicModel,
    when_to_use="Use the BasicModel for straightforward, direct recall of factual information such as definitions, dates, or simple equations.",
    when_not_to_use="Do not use the BasicModel for complex concepts requiring deeper understanding or extensive context.",
    how_to_use="Create a prompt on the Front of the flashcard that asks a direct question or requests a definition, and provide a clear, concise answer on the Back.",
    examples=[
        BasicModel(Front="Principle that allows planes to fly", Back="Bernoulli's principle"),
        BasicModel(Front="Atomic number of oxygen", Back="8")
    ],
    counter_examples=[
        BasicModel(Front="Causes of the French Revolution", Back="Too complex for a BasicModel."),
        BasicModel(Front="Process of photosynthesis", Back="Too complex for a BasicModel.")
    ]
)

BasicAndReversedNote = NoteModel(
    type="Basic (and reversed card)",
    model=BasicAndReversedModel,
    when_to_use="Use when both forward and reverse recall are beneficial, such as with vocabulary or fundamental concepts where both the concept and its description are equally important.",
    when_not_to_use="Avoid using this model for detailed explanations or scenarios where context cannot be reversed simply.",
    how_to_use="Each side should clearly correspond to the other, facilitating recall from either direction.",
    examples=[
        BasicAndReversedModel(Front="listName.get(i)", Back="Retrieves the element at index i from a list."),
        BasicAndReversedModel(Front="Paris", Back="Capital of France")
    ],
    counter_examples=[
        BasicAndReversedModel(Front="Grey wolf subspecies", Back="This is ambiguous when reversed."),
        BasicAndReversedModel(Front="Explain the French Revolution", Back="Too complex to reverse.")
    ]
)

BasicTypeInAnswerNote = NoteModel(
    type="Basic (type in the answer)",
    model=BasicTypeInAnswerModel,
    when_to_use="Ideal for practicing exact recall of terms, dates, or specific facts that benefit from active user input.",
    when_not_to_use="Not suitable for answers that are lengthy, have multiple correct responses, or are subjective.",
    how_to_use="Questions should be framed to yield a specific, brief answer, enhancing retention through typing.",
    examples=[
        BasicTypeInAnswerModel(Front="Year the Berlin Wall fell", Back="1989"),
        BasicTypeInAnswerModel(Front="First element on the periodic table", Back="Hydrogen")
    ],
    counter_examples=[
        BasicTypeInAnswerModel(Front="List the causes of World War I", Back="Too complex with multiple valid responses."),
        BasicTypeInAnswerModel(Front="What makes a great leader?", Back="Subjective and cannot be answered definitively or briefly.")
    ]
)

ClozeNote = NoteModel(
    type="Cloze",
    model=ClozeModel,
    when_to_use="Best used when context around the cloze deletion aids in the recall of the missing word or phrase. Suitable for language learning, detailed processes, or when partial knowledge testing is beneficial.",
    when_not_to_use="Avoid for overly simplistic or overly complex texts where cloze deletions do not naturally fit or enhance learning.",
    how_to_use="Write a coherent, meaningful sentence or paragraph with strategic deletions highlighted. Include extra information on the back to further clarify the context or provide additional learning material.",
    examples=[
        ClozeModel(Text="The {{c1::heart}} pumps blood throughout the {{c2::circulatory system}}.", Extra="Describes the basic function of a vital organ."),
        ClozeModel(Text="Python utilizes {{c1::indentation}} to define the bounds of code blocks.", Extra="Reflects a fundamental aspect of Python syntax.")
    ],
    counter_examples=[
        ClozeModel(Text="Photosynthesis is {{c1::important}}.", Extra="Too vague; doesn't effectively use the cloze method."),
        ClozeModel(Text="He mentioned {{c1::something}}.", Extra="Too ambiguous; lacks context.")
    ]
)


def QuestionGenerator(questioning_chunks, questioning_context):
    parser = PydanticOutputParser(pydantic_object=Questions)
    prompt = PromptTemplate(
    template="""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
    You are a question generating study assistant.
    You aim to generate a List of questions regarding the provided document.\n
    1. The questions should be designed to help the user study the key concept, terms, definitions, important points, context, and content of the document very well. \n
    2. They should aim to be clear, concise, and relevant to the document. \n
    3. They should be designed to help the user gain a deep understanding of the document. \n
    4. They should prompt the user to apply the knowledge learned from the document. \n
    5. They should be in English. \n
    6. They should NOT be about trivial details or irrelevant information. \n
    7. They should NOT be too broad or too narrow. \n
    8. They should NOT be subjective or opinion-based. \n
    9. They should NOT be ambiguous or confusing. \n
    10. They should NOT be leading or biased. \n\n

    Try to come up with as many questions as you can think of. If you think you have enough questions, examine the document again and see if you can come up with more questions. \n\n
    
    Be mindful of what the user wants you to focus on in the document and the context of the questioning provided. \n\n

    Here is the document: \n\n {document} \n\n

    {format_instructions}
    <|eot_id|><|start_header_id|>user<|end_header_id|>
    questioning context: \n\n
    '''\n
    {questioning_context}\n
    '''\n
    <|eot_id|><|start_header_id|>assistant<|end_header_id|>
    """,
    input_variables=["question", "document"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
    )
    return (prompt | llm | parser.invoke({"document": questioning_chunks, "questioning_context": questioning_context}))

def QuestionsDeduplicator(questions):
    parser = JsonOutputParser(pydantic_object=Questions)
    prompt = PromptTemplate(
    template="""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
    You are a question deduplicator. 
    You aim to remove duplicate questions from the list of questions generated by the question generating study assistant. \n
    Remove any outright duplicates, questions that are too similar, questions that are asking the same thing in a different way, or have the same answer. \n
    Keep the questions that are unique, clear, concise, and relevant to the document. \n

    Provide the COMPLETE list of remaining questions with duplicates removed! Once you have listed all the questions, inspect the list you have provided for more 
    valid questions you could add and do that.\n
    Respond ONLY with the list of questions, no preamble or explanation needed. \n\n

    questions: \n\n
    '''\n
    {questions}\n
    '''\n
    <|eot_id|><|start_header_id|>assistant<|end_header_id|>
    """,
    input_variables=["questions"],
    )
    return (prompt | llm | parser.invoke({"questions": questions}))

#Should model a dict that has the note type and then a list of the INDICES of the questions and answers for that note type
def ExpertRouterModel(BaseModel):
    Basic: List[int] = Field(description="A List of the indices of the question and answer pairs provided to you that should use the 'Basic' Note Type")
    BasicAndReversed: List[int] = Field(description="A List of the indices of the question and answer pairs provided to you that should use the 'Basic (and reversed card)' Note Type")
    BasicTypeInAnswer: List[int] = Field(description="A List of the indices of the question and answer pairs provided to you that should use the 'Basic (type in the answer)' Note Type")
    Cloze: List[int] = Field(description="A List of the indices of the question and answer pairs provided to you that should use the 'Cloze' Note Type")


def ExpertRouter(questions_with_answers):
    parser = JsonOutputParser(pydantic_object=ExpertRouterModel)
    prompt = PromptTemplate(
    template="""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
    You are an expert router. 
    You aim to route the questions and answers to the appropriate note type for the user to study. \n
    You have been provided with a list of questions and answers. \n
    You should decide which note type each question and answer pair should be assigned to. \n
    Assign each question and answer pair to the appropriate note type. Make sure you assign every pair. \n
    Be mindful of assigning the questions and answers to the note type fitting them best. \n
    You use the guidelines provided to you for every note type to make your decision. \n\n

    GUIDELINES: \n
    Basic: {basic_when_to_use} \n
    {basic_when_not_to_use} \n
    {basic_examples} \n
    {basic_counter_examples} \n\n
    ------------------------------
    Basic (and reversed card): {basic_and_reversed_when_to_use} \n
    {basic_and_reversed_when_not_to_use} \n
    {basic_and_reversed_examples} \n
    {basic_and_reversed_counter_examples} \n\n
    ------------------------------
    Basic (type in the answer): {basic_type_in_answer_when_to_use} \n
    {basic_type_in_answer_when_not_to_use} \n
    {basic_type_in_answer_examples} \n
    {basic_type_in_answer_counter_examples} \n\n
    ------------------------------
    Cloze: {cloze_when_to_use} \n
    {cloze_when_not_to_use} \n
    {cloze_examples} \n
    {cloze_counter_examples} \n\n
    ------------------------------
    Here are the questions and answer pairs: \n\n
    '''\n
    {questions_with_answers}\n
    '''\n

    Provide a dict that has the note type and then a list of the INDICES of the questions and answers for that note type in the provided list. \n
    Format Instructions: {format_instructions} \n
    <|eot_id|><|start_header_id|>assistant<|end_header_id|>
    """,
    input_variables=["questions_with_answers", "basic_when_to_use", "basic_when_not_to_use", "basic_examples", "basic_counter_examples", "basic_and_reversed_when_to_use", "basic_and_reversed_when_not_to_use", "basic_and_reversed_examples", "basic_and_reversed_counter_examples", "basic_type_in_answer_when_to_use", "basic_type_in_answer_when_not_to_use", "basic_type_in_answer_examples", "basic_type_in_answer_counter_examples", "cloze_when_to_use", "cloze_when_not_to_use", "cloze_examples", "cloze_counter_examples"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
    )
    return (prompt | llm | parser.invoke({"questions_with_answers": questions_with_answers, "basic_when_to_use": BasicNote.when_to_use, "basic_when_not_to_use": BasicNote.when_not_to_use, "basic_examples": BasicNote.examples, "basic_counter_examples": BasicNote.counter_examples, "basic_and_reversed_when_to_use": BasicAndReversedNote.when_to_use, "basic_and_reversed_when_not_to_use": BasicAndReversedNote.when_not_to_use, "basic_and_reversed_examples": BasicAndReversedNote.examples, "basic_and_reversed_counter_examples": BasicAndReversedNote.counter_examples, "basic_type_in_answer_when_to_use": BasicTypeInAnswerNote.when_to_use, "basic_type_in_answer_when_not_to_use": BasicTypeInAnswerNote.when_not_to_use, "basic_type_in_answer_examples": BasicTypeInAnswerNote.examples, "basic_type_in_answer_counter_examples": BasicTypeInAnswerNote.counter_examples, "cloze_when_to_use": ClozeNote.when_to_use, "cloze_when_not_to_use": ClozeNote.when_not_to_use, "cloze_examples": ClozeNote.examples, "cloze_counter_examples": ClozeNote.counter_examples}))


def BasicNoteGenerator(question_with_answer):
    parser = PydanticOutputParser(pydantic_object=BasicModel)
    format_instructions = parser.get_format_instructions()
    prompt = PromptTemplate(
    template="""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
    You are a flashcard generator. 
    You create flashcards of the type 'Basic' for the user to study. \n
    You have been provided with a question and answer pair. \n
    Additionally you have been provided with guidelines for the 'Basic' note type. \n
    Using the guidelines provided, create a flashcard of the 'Basic' type. \n\n

    '''
    Questions and Answer:
    {question_with_answer}
    '''\n\n
    Flashcard Creation Guidelines: {how_to_use}\n
    Examples: {examples} \n
    Counter Examples: {counter_examples} \n
    Format Instructions: {format_instructions}
    <|eot_id|><|start_header_id|>assistant<|end_header_id|>""",
    input_variables=["question_with_answer", "how_to_use", "examples", "counter_examples"],
    partial_variables={"format_instructions": format_instructions},
    )
    return (prompt | llm | parser.invoke({"question_with_answer": question_with_answer, "how_to_use": BasicNote.how_to_use, "examples": BasicNote.examples, "counter_examples": BasicNote.counter_examples}))

def BasicAndReversedNoteGenerator(question_with_answer):
    parser = PydanticOutputParser(pydantic_object=BasicAndReversedModel)
    format_instructions = parser.get_format_instructions()
    prompt = PromptTemplate(
    template="""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
    You are a flashcard generator. 
    You create flashcards of the type 'Basic (and reversed card)' for the user to study. \n
    You have been provided with a question and answer pair. \n
    Additionally you have been provided with guidelines for the 'Basic (and reversed card)' note type. \n
    Using the guidelines provided, create a flashcard of the 'Basic (and reversed card)' type. \n\n

    '''
    Questions and Answer:
    {question_with_answer}
    '''\n\n
    Flashcard Creation Guidelines: {how_to_use}\n
    Examples: {examples} \n
    Counter Examples: {counter_examples} \n
    Format Instructions: {format_instructions}
    <|eot_id|><|start_header_id|>assistant<|end_header_id|>""",
    input_variables=["question_with_answer", "how_to_use", "examples", "counter_examples"],
    partial_variables={"format_instructions": format_instructions},
    )
    return (prompt | llm | parser.invoke({"question_with_answer": question_with_answer, "how_to_use": BasicAndReversedNote.how_to_use, "examples": BasicAndReversedNote.examples, "counter_examples": BasicAndReversedNote.counter_examples}))

def BasicTypeInAnswerNoteGenerator(question_with_answer):
    parser = PydanticOutputParser(pydantic_object=BasicTypeInAnswerModel)
    format_instructions = parser.get_format_instructions()
    prompt = PromptTemplate(
    template="""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
    You are a flashcard generator. 
    You create flashcards of the type 'Basic (type in the answer)' for the user to study. \n
    You have been provided with a question and answer pair. \n
    Additionally you have been provided with guidelines for the 'Basic (type in the answer)' note type. \n
    Using the guidelines provided, create a flashcard of the 'Basic (type in the answer)' type. \n\n

    '''
    Questions and Answer:
    {question_with_answer}
    '''\n\n
    Flashcard Creation Guidelines: {how_to_use}\n
    Examples: {examples} \n
    Counter Examples: {counter_examples} \n
    Format Instructions: {format_instructions}
    <|eot_id|><|start_header_id|>assistant<|end_header_id|>""",
    input_variables=["question_with_answer", "how_to_use", "examples", "counter_examples"],
    partial_variables={"format_instructions": format_instructions},
    )
    return (prompt | llm | parser.invoke({"question_with_answer": question_with_answer, "how_to_use": BasicTypeInAnswerNote.how_to_use, "examples": BasicTypeInAnswerNote.examples, "counter_examples": BasicTypeInAnswerNote.counter_examples}))

def ClozeNoteGenerator(question_with_answer):
    parser = PydanticOutputParser(pydantic_object=ClozeModel)
    format_instructions = parser.get_format_instructions()
    prompt = PromptTemplate(
    template="""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
    You are a flashcard generator. 
    You create flashcards of the type 'Cloze' for the user to study. \n
    You can write cloze deletions like so: {{c1::text}}, {{c2::text2}}, ... \n
    You have been provided with a question and answer pair. \n
    Additionally you have been provided with guidelines for the 'Cloze' note type. \n
    Using the guidelines provided, create a flashcard of the 'Cloze' type. \n\n

    '''
    Questions and Answer:
    {question_with_answer}
    '''\n\n
    Flashcard Creation Guidelines: {how_to_use}\n
    Examples: {examples} \n
    Counter Examples: {counter_examples} \n
    Format Instructions: {format_instructions}
    <|eot_id|><|start_header_id|>assistant<|end_header_id|>""",
    input_variables=["question_with_answer", "how_to_use", "examples", "counter_examples"],
    partial_variables={"format_instructions": format_instructions},
    )
    return (prompt | llm | parser.invoke({"question_with_answer": question_with_answer, "how_to_use": ClozeNote.how_to_use, "examples": ClozeNote.examples, "counter_examples": ClozeNote.counter_examples}))