#from langchain_nvidia_ai_endpoints import ChatNVIDIA
#from langchain_core.prompts import PromptTemplate
#from langchain_core.output_parsers import JsonOutputParser
#from apiUtils.key_manager import get_api_key
#from ankiUtils.note_models import NoteModel, BasicModel
#
##TODO make this more abstract and move the concrete prompts, outtput parser and so on to a different file
#model_id = "meta/llama3-70b-instruct"
#api_key = get_api_key()
#llm = ChatNVIDIA(model=model_id, nvidia_api_key=api_key, temperature=0)
#
#def generate_card(source_material: str, note_model: NoteModel) -> BasicModel:
#    parser = JsonOutputParser(pydantic_object=note_model.model)
#    prompt = PromptTemplate(
#    template="""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
#    You are a flashcard generator. 
#    You pick ONE fact from the source material to create a flashcard out of.
#    Flashcard Creation Guidelines: {how_to_use}
#    Examples: {examples}
#    Counter Examples: {counter_examples}
#    Source Material: {source_material}
#    {format_instructions}
#    <|eot_id|><|start_header_id|>assistant<|end_header_id|>""",
#    input_variables=["question", "how_to_use", "examples", "counter_examples"],
#    partial_variables={"format_instructions": parser.get_format_instructions()},
#    )
#    chain = prompt | llm | parser
#    generation = chain.invoke({"source_material": source_material, "how_to_use": note_model.how_to_use, "examples": note_model.examples, "counter_examples": note_model.counter_examples})
#    return generation