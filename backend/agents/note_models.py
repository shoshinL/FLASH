from typing import List, Type
from pydantic import BaseModel, Field

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