from typing import List, Type
from langchain_core.output_parsers import PydanticOutputParser, JsonOutputParser
from langchain.output_parsers import OutputFixingParser
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field
from venv import logger

from settingUtils.api_key_utils import require_llm

class Questions(BaseModel):
    Questions: List[str] = Field(description="A List of questions to be asked for studying the key points, terms, definitions, facts, context, and content of the provided document (paper, study notes, lecture slides, ...) very well.")

class QuestionWithAnswer(BaseModel):
    Question: str = Field(description="A Question to be asked for studying the key points, terms, definitions, facts, context, and content of a document (paper, study notes, lecture slides, ...) very well.")
    Answer: str = Field(description="The answer to the question with context and explanation.")

class BasicModel(BaseModel):
    Type: str = Field(description="The type of the flashcard. Should be 'Basic'.")
    Front: str = Field(description="The front of the flashcard.")
    Back: str = Field(description="The back of the flashcard.")

class BasicAndReversedModel(BaseModel):
    Type: str = Field(description="The type of the flashcard. Should be 'Basic (and reversed card)'.")
    Front: str = Field(description="The front/back of the reversible flashcard.")
    Back: str = Field(description="The back/front of the reversible flashcard.")

class BasicTypeInAnswerModel(BaseModel):
    Type: str = Field(description="The type of the flashcard. Should be 'Basic (type in the answer)'.")
    Front: str = Field(description="The front of the flashcard.")
    Back: str = Field(description="The back of the flashcard. This needs to be typed in by the user. Should be very short.")    

class ClozeModel(BaseModel):
    Type: str = Field(description="The type of the flashcard. Should be 'Cloze'.")
    Text: str = Field(description="The text of the cloze flashcard. You can use {{c1::text}}, {{c2::text2}}, ... to create a cloze deletion.")
    BackExtra: str = Field(description="Extra information to be displayed on the back of the cloze flashcard. Optional.")

class NotePromptModel:
    type: str
    when_to_use: str
    when_not_to_use: str
    how_to_use: str
    examples: List[BasicModel]
    counter_examples: List[BasicModel]

    def __init__(self, type: str, when_to_use: str, when_not_to_use: str, how_to_use: str, examples: List[Type[BaseModel]], counter_examples: List[Type[BaseModel]]):
        self.type = type
        self.when_to_use = when_to_use
        self.when_not_to_use = when_not_to_use
        self.how_to_use = how_to_use
        self.examples = examples
        self.counter_examples = counter_examples


BasicNote = NotePromptModel(
    type="Basic",
    when_to_use="Use the BasicModel for straightforward, direct recall of factual information such as definitions, dates, or simple equations.",
    when_not_to_use="Do not use the BasicModel for complex concepts requiring deeper understanding or extensive context.",
    how_to_use="Create a prompt on the Front of the flashcard that asks a direct question or requests a definition, and provide a clear, concise answer on the Back.",
    examples=[
        BasicModel(Type="Basic", Front="Principle that allows planes to fly", Back="Bernoulli's principle"),
        BasicModel(Type="Basic", Front="Atomic number of oxygen", Back="8")
    ],
    counter_examples=[
        BasicModel(Type="Basic",Front="Causes of the French Revolution", Back="Too complex for a BasicModel."),
        BasicModel(Type="Basic",Front="Process of photosynthesis", Back="Too complex for a BasicModel.")
    ]
)

BasicAndReversedNote = NotePromptModel(
    type="Basic (and reversed card)",
    when_to_use="Use when both forward and reverse recall are beneficial, such as with vocabulary or fundamental concepts where both the concept and its description are equally important.",
    when_not_to_use="Avoid using this model for detailed explanations or scenarios where context cannot be reversed simply.",
    how_to_use="Each side should clearly correspond to the other, facilitating recall from either direction.",
    examples=[
        BasicAndReversedModel(Type="Basic (and reversed card)", Front="listName.get(i)", Back="Retrieves the element at index i from a list."),
        BasicAndReversedModel(Type="Basic (and reversed card)", Front="Paris", Back="Capital of France")
    ],
    counter_examples=[
        BasicAndReversedModel(Type="Basic (and reversed card)", Front="Grey wolf subspecies", Back="This is ambiguous when reversed."),
        BasicAndReversedModel(Type="Basic (and reversed card)", Front="Explain the French Revolution", Back="Too complex to reverse.")
    ]
)

BasicTypeInAnswerNote = NotePromptModel(
    type="Basic (type in the answer)",
    when_to_use="Ideal for practicing exact recall of terms, dates, or specific facts that benefit from active user input.",
    when_not_to_use="Not suitable for answers that are lengthy, have multiple correct responses, or are subjective.",
    how_to_use="Questions should be framed to yield a specific, brief answer, enhancing retention through typing.",
    examples=[
        BasicTypeInAnswerModel(Type="Basic (type in the answer)", Front="Year the Berlin Wall fell", Back="1989"),
        BasicTypeInAnswerModel(Type="Basic (type in the answer)", Front="First element on the periodic table", Back="Hydrogen")
    ],
    counter_examples=[
        BasicTypeInAnswerModel(Type="Basic (type in the answer)", Front="List the causes of World War I", Back="Too complex with multiple valid responses."),
        BasicTypeInAnswerModel(Type="Basic (type in the answer)", Front="What makes a great leader?", Back="Subjective and cannot be answered definitively or briefly.")
    ]
)

ClozeNote = NotePromptModel(
    type="Cloze",
    when_to_use="Best used when context around the cloze deletion aids in the recall of the missing word or phrase.",
    when_not_to_use="Avoid for overly simplistic or overly complex texts where cloze deletions do not naturally fit or enhance learning. Should not be used for lists/enumerations!",
    how_to_use="Write a coherent, meaningful sentence or paragraph with strategic deletions highlighted. Include extra information on the back to further clarify the context or provide additional learning material.",
    examples=[
        ClozeModel(Type="Cloze", Text="The {{c1::heart}} pumps blood throughout the {{c2::circulatory system}}.", BackExtra="Describes the basic function of a vital organ."),
        ClozeModel(Type="Cloze", Text="Python utilizes {{c1::indentation}} to define the bounds of code blocks.", BackExtra="Reflects a fundamental aspect of Python syntax.")
    ],
    counter_examples=[
        ClozeModel(Type="Cloze", Text="Photosynthesis is {{c1::important}}.", BackExtra="Too vague; doesn't effectively use the cloze method."),
        ClozeModel(Type="Cloze", Text="He mentioned {{c1::something}}.", BackExtra="Too ambiguous; lacks context.")
    ]
)

ListNote = NotePromptModel(
    type="Cloze",
    when_to_use="Best used for all enumerations, lists of items, steps, or concepts that benefit from sequential recall.",
    when_not_to_use="Avoid for unrelated items, items that are not in an enumeration or list format, or items that are very long",
    how_to_use="List items in a logical order, with each item clearly separated and numbered. Each item should be a cloze deletion in a html table. Include extra information on the back to provide context or further explanation.",
    examples=[
        ClozeModel(Type="Cloze", Text="The 3 values of the french revolution:\n <ol>\n<li>{{c1::Liberté (Liberty)}}</li>\n<li>{{c2::Égalité (Equality)}}</li>\n<li>{{c3::Fraternité (Fraternity)}}</li>\n</ol>", BackExtra="These values formed the ideological foundation for modern democratic societies, emphasizing the importance of individual freedoms, social justice, and solidarity."),
        ClozeModel(Type="Cloze", Text="The 5 steps of the scientific method:\n <ol>\n<li>{{c1::Observation}}</li>\n<li>{{c2::Hypothesis}}</li>\n<li>{{c3::Prediction}}</li>\n<li>{{c4::Experiment}}</li>\n<li>{{c5::Conclusion}}</li>\n</ol>", BackExtra="This method is used to investigate natural phenomena, establish cause-and-effect relationships, and refine scientific knowledge.")
    ],
    counter_examples=[
        ClozeModel(Type="Cloze", Text="The best colors are:\n <ol>\n<li>{{c1::Blue}}</li>\n<li>{{c2::Green}}</li>\n<li>{{c3::Red}}</li>\n</ol>", BackExtra="Is vague and not suitable for a list note."),
        ClozeModel(Type="Cloze", Text="Stealing is:\n <ol>\n<li>{{c1::Bad}}</li>\n<li>{{c2::Good}}</li>\n</ol>", BackExtra="Is not a list of items.")
    ]
)


@require_llm
def QuestionGenerator(llm, questioning_chunk, n_questions, questioning_context):
    logger.debug("Starting QuestionGenerator")
    parser = JsonOutputParser(pydantic_object=Questions)
    fixing_parser = OutputFixingParser.from_llm(llm=llm, parser=parser, max_retries=1)
    prompt = PromptTemplate(
    template="""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
    You are a question generating study assistant.
    You aim to generate a List of questions regarding the provided document.
    1. The questions should be designed to help the user study the key concepts, terms, definitions, and important points of the document very well. 
    2. They should aim to be clear, concise, and relevant to the document. 
    3. They should be designed to help the user gain a deep understanding of the document. 
    4. They should be fit for generating short flashcards for studying the document in terms of size and context. 
    5. They should prompt the user to apply the knowledge learned from the document. 
    6. They should ask for only one piece of information at a time.
    7. They should be in English. 
    8. They should NOT be about trivial details or irrelevant information. 
    9. They should NOT be too broad or too narrow. 
    10. They should NOT be subjective or opinion-based. 
    11. They should NOT be ambiguous or confusing. 
    12. They should NOT be leading or biased.

    Be mindful of what the user wants you to focus on in the document and the context of the questioning provided.

    GENERATE EXACTLY {n_questions}! ONLY MAKE {n_questions} QUESTION!

    Here is the document: \n\n {document} \n\n

    {format_instructions}
    <|eot_id|><|start_header_id|>user<|end_header_id|>
    questioning context:
    '''
    {questioning_context}\n
    '''
    <|eot_id|><|start_header_id|>assistant<|end_header_id|>
    """,
    input_variables=["document", "n_questions", "questioning_context"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    chain = prompt | llm | fixing_parser
    result = chain.invoke({"document": questioning_chunk, "n_questions": n_questions, "questioning_context": questioning_context})
    logger.debug(f"Generated Questions: {result}")
    
    return result

@require_llm
def QuestionsDeduplicator(llm, questions, n_questions):
    logger.debug("Starting QuestionsDeduplicator")
    parser = JsonOutputParser(pydantic_object=Questions)
    fixing_parser = OutputFixingParser.from_llm(llm=llm, parser=parser, max_retries=1)
    prompt = PromptTemplate(
    template="""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
    You are a question deduplicator. 
    You aim to remove duplicate questions from the list of questions generated by the question generating study assistant. 
    Remove any outright duplicates, questions that are too similar, questions that are asking the same thing in a different way, or have the same answer. 
    Keep the questions that are unique, clear, concise, and relevant to the document. 

    Provide the COMPLETE list of remaining questions with duplicates removed! Once you have listed all the questions, inspect the list you have provided for more 
    valid questions you could add and do that.
    Respond ONLY with the list of questions, no preamble or explanation needed. \n

    GENERATE EXACTLY {n_questions}! ONLY MAKE {n_questions} QUESTION!

    questions: \n
    '''
    {questions}\n
    '''\n
    {format_instructions}
    <|eot_id|><|start_header_id|>assistant<|end_header_id|>
    """,
    input_variables=["questions", "n_questions"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
    )
    chain = prompt | llm | fixing_parser
    result = chain.invoke({"questions": questions, "n_questions": n_questions})
    logger.debug(f"Deduplicated Questions: {result}")
    return result

class ExpertRouterModel(BaseModel):
    Basic: List[int] = Field(description="A List of the indices of the question and answer pairs provided to you that should use the 'Basic' Note Type")
    BasicAndReversed: List[int] = Field(description="A List of the indices of the question and answer pairs provided to you that should use the 'Basic (and reversed card)' Note Type")
    BasicTypeInAnswer: List[int] = Field(description="A List of the indices of the question and answer pairs provided to you that should use the 'Basic (type in the answer)' Note Type")
    Cloze: List[int] = Field(description="A List of the indices of the question and answer pairs provided to you that should use the 'Cloze' Note Type")
    ItemList: List[int] = Field(description="A List of the indices of the question and answer pairs provided to you that should use the 'List' Note Type") # type: ignore

@require_llm
def ExpertRouter(llm, questions_with_answers):
    logger.debug("Starting ExpertRouter")
    parser = PydanticOutputParser(pydantic_object=ExpertRouterModel)
    fixing_parser = OutputFixingParser.from_llm(llm=llm, parser=parser, max_retries=1)
    prompt = PromptTemplate(
        template="""system
        You are an expert in routing question-answer pairs to flashcard note types.
        Your goal is to assign each question and answer pair to the most suitable note type for effective study.
        You have been provided with a list of questions and answers, and your task is to determine the appropriate note type for each pair based on the information to be learned.

        GUIDELINES:

            Basic: {basic_when_to_use}
                {basic_when_not_to_use}
                {basic_examples}
                {basic_counter_examples}

            Basic (and reversed card): {basic_and_reversed_when_to_use}
                {basic_and_reversed_when_not_to_use}
                {basic_and_reversed_examples}
                {basic_and_reversed_counter_examples}

            Basic (type in the answer): {basic_type_in_answer_when_to_use}
                {basic_type_in_answer_when_not_to_use}
                {basic_type_in_answer_examples}
                {basic_type_in_answer_counter_examples}

            Cloze: {cloze_when_to_use}
                {cloze_when_not_to_use}
                {cloze_examples}
                {cloze_counter_examples}

            ItemList: {list_when_to_use}
                {list_when_not_to_use}
                {list_examples}
                {list_counter_examples}

        TASK:

            1. Review each question and answer pair.
            2. Assign each pair to one of the following note types: Basic, BasicAndReversed, BasicTypeInAnswer, Cloze, or ItemList.
            3. Ensure every pair is assigned a note type based on the guidelines provided.

        Here are the questions and answer pairs:
        '''
        {questions_with_answers}
        '''

        The sum of the length of all the lists should be {n_questions}!
        Provide the response in the requested format without any preamble or explanation.

        FORMAT:
        {format_instructions}
        """,
        input_variables=[
            "questions_with_answers", "basic_when_to_use", "basic_when_not_to_use", 
            "basic_examples", "basic_counter_examples", "basic_and_reversed_when_to_use", 
            "basic_and_reversed_when_not_to_use", "basic_and_reversed_examples", 
            "basic_and_reversed_counter_examples", "basic_type_in_answer_when_to_use", 
            "basic_type_in_answer_when_not_to_use", "basic_type_in_answer_examples", 
            "basic_type_in_answer_counter_examples", "cloze_when_to_use", "cloze_when_not_to_use", 
            "cloze_examples", "cloze_counter_examples", "list_when_to_use", 
            "list_when_not_to_use", "list_examples", "list_counter_examples",
            "n_questions"
        ],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )
    
    chain = prompt | llm | fixing_parser
    
    result = chain.invoke({
        "questions_with_answers": questions_with_answers, 
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
        "list_counter_examples": ListNote.counter_examples,
        "n_questions": len(questions_with_answers)
    })
    logger.debug(f"Assigned Note Types: {result}") 
    return result


@require_llm
def BasicNoteGenerator(llm, question_with_answer):
    parser = JsonOutputParser(pydantic_object=BasicModel)
    fixing_parser = OutputFixingParser.from_llm(llm=llm, parser=parser, max_retries=1)    
    format_instructions = parser.get_format_instructions()
    prompt = PromptTemplate(
    template="""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
    You are a flashcard generator. 
    You create flashcards of the type '{type}' for the user to study. \n
    The card should be short. It's fine to not use every information provided. \n
    The card should contain a prompt instead of a question. Example: "Capital of Paris" instead of "What is the capital of Paris?" \n
    You have been provided with a question and answer pair. \n
    Additionally you have been provided with guidelines for the '{type}' note type. \n
    Using the guidelines provided, create a flashcard of the '{type}' type. \n\n

    '''
    Questions and Answer:
    {question_with_answer}
    '''\n\n
    Flashcard Creation Guidelines: {how_to_use}\n
    Examples: {examples} \n
    Counter Examples: {counter_examples} \n

    Provide the response in the requested format without any preamble or explanation.
    Format Instructions: {format_instructions}
    <|eot_id|><|start_header_id|>assistant<|end_header_id|>""",
    input_variables=["type", "question_with_answer", "how_to_use", "examples", "counter_examples"],
    partial_variables={"format_instructions": format_instructions},
    )
    chain = prompt | llm | fixing_parser
    return chain.invoke({"question_with_answer": question_with_answer, "type": BasicNote.type, "how_to_use": BasicNote.how_to_use, "examples": BasicNote.examples, "counter_examples": BasicNote.counter_examples})

@require_llm
def BasicAndReversedNoteGenerator(llm, question_with_answer):
    parser = JsonOutputParser(pydantic_object=BasicAndReversedModel)
    fixing_parser = OutputFixingParser.from_llm(llm=llm, parser=parser, max_retries=1)
    format_instructions = parser.get_format_instructions()
    prompt = PromptTemplate(
    template="""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
    You are a flashcard generator. 
    You create flashcards of the type '{type}' for the user to study. \n
    The front and back of the card should be reversible. Make sure that they do not need additonal context.\n
    The card should be short. It's fine to not use every information provided. \n
    The card should contain a prompt instead of a question. Example: "Capital of Paris" instead of "What is the capital of Paris?" \n
    You have been provided with a question and answer pair. \n
    Additionally you have been provided with guidelines for the '{type}' note type. \n
    Using the guidelines provided, create a flashcard of the '{type}' type. \n\n

    '''
    Questions and Answer:
    {question_with_answer}
    '''\n\n
    Flashcard Creation Guidelines: {how_to_use}\n
    Examples: {examples} \n
    Counter Examples: {counter_examples} \n

    Provide the response in the requested format without any preamble or explanation.
    Format Instructions: {format_instructions}
    <|eot_id|><|start_header_id|>assistant<|end_header_id|>""",
    input_variables=["type", "question_with_answer", "how_to_use", "examples", "counter_examples"],
    partial_variables={"format_instructions": format_instructions},
    )
    chain = prompt | llm | fixing_parser
    return chain.invoke({"question_with_answer": question_with_answer, "type": BasicAndReversedNote.type, "how_to_use": BasicAndReversedNote.how_to_use, "examples": BasicAndReversedNote.examples, "counter_examples": BasicAndReversedNote.counter_examples})

@require_llm
def BasicTypeInAnswerNoteGenerator(llm, question_with_answer):
    parser = JsonOutputParser(pydantic_object=BasicTypeInAnswerModel)
    fixing_parser = OutputFixingParser.from_llm(llm=llm, parser=parser, max_retries=1)
    format_instructions = parser.get_format_instructions()
    prompt = PromptTemplate(
    template="""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
    You are a flashcard generator. 
    You create flashcards of the type '{type}' for the user to study. \n
    You have been provided with a question and answer pair. \n
    The card should be short. It's fine to not use every information provided. \n
    The card should contain a prompt instead of a question. Example: "Capital of Paris" instead of "What is the capital of Paris?" \n
    The answer/back should be only one word!
    Additionally you have been provided with guidelines for the '{type}' note type. \n
    Using the guidelines provided, create a flashcard of the '{type}' type. \n\n

    '''
    Questions and Answer:
    {question_with_answer}
    '''\n\n
    Flashcard Creation Guidelines: {how_to_use}\n
    Examples: {examples} \n
    Counter Examples: {counter_examples} \n

    Provide the response in the requested format without any preamble or explanation.
    Format Instructions: {format_instructions}
    <|eot_id|><|start_header_id|>assistant<|end_header_id|>""",
    input_variables=["type", "question_with_answer", "how_to_use", "examples", "counter_examples"],
    partial_variables={"format_instructions": format_instructions},
    )
    chain = prompt | llm | fixing_parser
    return chain.invoke({"question_with_answer": question_with_answer, "type": BasicTypeInAnswerNote.type, "how_to_use": BasicTypeInAnswerNote.how_to_use, "examples": BasicTypeInAnswerNote.examples, "counter_examples": BasicTypeInAnswerNote.counter_examples})

@require_llm
def ClozeNoteGenerator(llm, question_with_answer):
    parser = JsonOutputParser(pydantic_object=ClozeModel)
    fixing_parser = OutputFixingParser.from_llm(llm=llm, parser=parser, max_retries=1)
    format_instructions = parser.get_format_instructions()
    prompt = PromptTemplate(
    template="""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
    You are a flashcard generator. 
    You create flashcards of the type '{type}' for the user to study. \n
    You NEED to write at least one cloze deletion. \n
    The card should be short. It's fine to not use every information provided. \n
    Focus on the main information. It should be one relatively short sentence. Focus on one key information!\n
    The card should contain a prompt instead of a question. Example: "Capital of Paris" instead of "What is the capital of Paris?" \n
    You have been provided with a question and answer pair. \n
    Additionally you have been provided with guidelines for the '{type}' note type. \n
    Using the guidelines provided, create a flashcard of the '{type}' type. \n\n

    '''
    Questions and Answer:
    {question_with_answer}
    '''\n\n
    Flashcard Creation Guidelines: {how_to_use}\n
    Examples: {examples} \n
    Counter Examples: {counter_examples} \n

    Provide the response in the requested format without any preamble or explanation.
    Format Instructions: {format_instructions}
    <|eot_id|><|start_header_id|>assistant<|end_header_id|>""",
    input_variables=["type", "question_with_answer", "how_to_use", "examples", "counter_examples"],
    partial_variables={"format_instructions": format_instructions},
    )
    chain = prompt | llm | fixing_parser
    data = chain.invoke({"question_with_answer": question_with_answer, "type": ClozeNote.type, "how_to_use": ClozeNote.how_to_use, "examples": ClozeNote.examples, "counter_examples": ClozeNote.counter_examples})
    data["Back Extra"] = data.pop("BackExtra")
    return data

@require_llm
def ListNoteGenerator(llm, question_with_answer):
    parser = JsonOutputParser(pydantic_object=ClozeModel)
    fixing_parser = OutputFixingParser.from_llm(llm=llm, parser=parser, max_retries=1)
    format_instructions = parser.get_format_instructions()
    prompt = PromptTemplate(
    template="""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
    You are a flashcard generator. 
    You create flashcards of the type '{type}' for the user to study. \n
    You NEED to make a list! \n
    You NEED to write a cloze deletion for every item in the list. \n
    The card should be short. It's fine to not use every information provided. \n
    The card should contain a prompt instead of a question. Example: "Capital of Paris" instead of "What is the capital of Paris?" \n
    You have been provided with a question and answer pair. \n
    Additionally you have been provided with guidelines for the '{type}' note type. \n
    Using the guidelines provided, create a flashcard of the '{type}' type. \n\n

    '''
    Questions and Answer:
    {question_with_answer}
    '''\n\n
    Flashcard Creation Guidelines: {how_to_use}\n
    Examples: {examples} \n
    Counter Examples: {counter_examples} \n

    Provide the response in the requested format without any preamble or explanation.
    Format Instructions: {format_instructions}
    <|eot_id|><|start_header_id|>assistant<|end_header_id|>""",
    input_variables=["type", "question_with_answer", "how_to_use", "examples", "counter_examples"],
    partial_variables={"format_instructions": format_instructions},
    )
    chain = prompt | llm | fixing_parser
    data = chain.invoke({"question_with_answer": question_with_answer, "type": ListNote.type, "how_to_use": ListNote.how_to_use, "examples": ListNote.examples, "counter_examples": ListNote.counter_examples})
    data["Back Extra"] = data.pop("BackExtra")
    return data