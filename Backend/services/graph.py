from typing import TypedDict

from langgraph.graph import StateGraph, END

from services.analyzer import analyze_content


class GraphState(TypedDict):
    content: str
    result: dict


# Node 1
def detect_input_node(state):
    print("Detect Input Node")
    return state


# Node 2
def analyze_node(state):

    result = analyze_content(
        state["content"]
    )

    return {
        "content": state["content"],
        "result": result
    }


# Build Graph
builder = StateGraph(GraphState)

builder.add_node(
    "detect_input",
    detect_input_node
)

builder.add_node(
    "analyze",
    analyze_node
)

builder.set_entry_point(
    "detect_input"
)

builder.add_edge(
    "detect_input",
    "analyze"
)

builder.add_edge(
    "analyze",
    END
)

graph = builder.compile()


def run_graph(content: str):

    result = graph.invoke({
        "content": content,
        "result": {}
    })

    return result["result"]