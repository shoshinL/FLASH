from typing import List, Type
from pydantic import BaseModel, Field
from .collection_manager import get_model_id, get_model_fields

#These models are mainly for the LLM agents
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
    Extra: str = Field(description="Extra information to be displayed on the back of the cloze flashcard. Optional.")

class NoteModel:
    anki_id: int
    type: str
    model: Type[BaseModel]
    when_to_use: str
    when_not_to_use: str
    how_to_use: str
    examples: List[BasicModel]
    counter_examples: List[BasicModel]

    def __init__(self, type: str, model: Type[BaseModel], when_to_use: str, when_not_to_use: str, how_to_use: str, examples: List[Type[BaseModel]], counter_examples: List[Type[BaseModel]]):
        self.type = type
        self.anki_id = get_model_id(self.type)
        self.model = model
        self.when_to_use = when_to_use
        self.when_not_to_use = when_not_to_use
        self.how_to_use = how_to_use
        self.examples = examples
        self.counter_examples = counter_examples

    @property
    def valid(self):
        anki_model_fields = get_model_fields(self.anki_id)
        for i, field in enumerate(self.model.model_fields.keys()):
            if field != anki_model_fields[i]:
                return False
        else: return True


