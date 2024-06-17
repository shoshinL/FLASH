import operator
from typing import Annotated, List

from typing_extensions import TypedDict

from langgraph.graph import StateGraph
from langgraph.constants import Send

class ChildState(TypedDict):
    question: int
    answers: List[int]

class ParentState(TypedDict):
    questioning: List[bool]
    answers: Annotated[List[bool], operator.add]

def child_start1(state: ChildState):
    return {"answers": [state["question"]]}

def child_start2(state: ChildState):
    return {"answers": [-state["question"]]}

child_builder1 = StateGraph(ChildState)
child_builder1.add_node("child_start", child_start1)
child_builder1.set_entry_point("child_start")
child_builder1.set_finish_point("child_start")  

child_builder2 = StateGraph(ChildState)
child_builder2.add_node("child_start", child_start2)
child_builder2.set_entry_point("child_start")
child_builder2.set_finish_point("child_start")

def end_parent(state: ParentState):
    return {"questioning": state["questioning"] + state["answers"]}

parent_builder = StateGraph(ParentState)
parent_builder = StateGraph(ParentState)
parent_builder.add_node("parent_start", lambda state: {"questioning": [1, -1, 2, -2]})
parent_builder.add_node("child1", child_builder1.compile())
parent_builder.add_node("child2", child_builder2.compile())
parent_builder.add_node("end_parent", end_parent)

def map_questioning(state: ParentState):
    return [Send("child1", {"question": question}) for question in state["questioning"] if question > 0] + [Send("child2", {"question": question}) for question in state["questioning"] if question < 0]

parent_builder.set_entry_point("parent_start")
parent_builder.add_conditional_edges("parent_start", map_questioning)
parent_builder.add_edge("child1", "end_parent")
parent_builder.add_edge("child2", "end_parent")
parent_builder.set_finish_point("end_parent")
graph = parent_builder.compile()

graph.invoke({"questioning": [True, True, False, True]}, debug=True)



"""
parser = PydanticOutputParser(pydantic_object=Questions)
format_instructions = parser.get_format_instructions()
prompt = ChatPromptTemplate(
    messages=[
        HumanMessagePromptTemplate.from_template("answer the users question as best as possible.\n{format_instructions}\n{question}")  
    ],
    input_variables=["question"],
    partial_variables={"format_instructions": format_instructions}
)
my_output = parser.parse(output.content)
"""