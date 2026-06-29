from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from collections import deque, defaultdict
import json

app = FastAPI()

# Allow the React dev server (localhost:3000) to call this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"Ping": "Pong"}


def is_dag(nodes, edges):
    """Return True if the graph has no cycles, using Kahn's algorithm.

    We repeatedly remove nodes that have no incoming edges. If we manage to
    remove every node, there is no cycle. If some nodes are left, they form
    a loop, so it is not a DAG.
    """
    indegree = {node["id"]: 0 for node in nodes}
    adjacency = defaultdict(list)

    for edge in edges:
        source, target = edge["source"], edge["target"]
        adjacency[source].append(target)
        if target in indegree:
            indegree[target] += 1

    queue = deque(node_id for node_id, count in indegree.items() if count == 0)
    visited = 0

    while queue:
        current = queue.popleft()
        visited += 1
        for neighbour in adjacency[current]:
            if neighbour in indegree:
                indegree[neighbour] -= 1
                if indegree[neighbour] == 0:
                    queue.append(neighbour)

    return visited == len(nodes)


@app.post("/pipelines/parse")
def parse_pipeline(nodes: str = Form(...), edges: str = Form(...)):
    nodes_list = json.loads(nodes)
    edges_list = json.loads(edges)

    return {
        "num_nodes": len(nodes_list),
        "num_edges": len(edges_list),
        "is_dag": is_dag(nodes_list, edges_list),
    }
