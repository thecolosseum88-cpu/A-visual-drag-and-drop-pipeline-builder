
A small visual pipeline builder. You drag nodes onto a canvas, connect them,
and submit the pipeline to a backend that reports how many nodes and edges it
has and whether it forms a valid DAG (no cycles).

The frontend is React with React Flow. The backend is Python with FastAPI.

## Running it

**Frontend**

```
cd frontend
npm i
npm start
```

Runs at http://localhost:3000.

**Backend** (in a separate terminal)

```
cd backend
python -m venv .env
.env\Scripts\activate        # on macOS/Linux: source .env/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Runs at http://localhost:8000.

## How it is built

### Node abstraction

Every node shares the same card layout, the same handle rendering, and the
same styling. Instead of repeating that in each file, all of it lives in one
component: `src/nodes/BaseNode.js`.

A node tells `BaseNode` three things: its title, its input/output handles, and
the fields to show inside it. Everything else is handled for it. As a result
each node file is short — usually around fifteen lines. Restyling every node,
or changing how handles are positioned, is a one-file change.

To show this off, the project includes five extra nodes beyond the original
four (Filter, Math, API Request, Note, Delay). They were quick to add because
of the abstraction, and they cover a range of shapes: one input, two inputs,
and a Note node with no handles at all.

Shared field styles live in `src/nodes/fieldStyles.js` so inputs and selects
look the same everywhere.

When you edit a field on a node, the value is saved back into that node's data
in the store (via `updateNodeField`), so it travels with the pipeline when you
submit.

### Styling

A single dark theme across the toolbar, canvas, nodes, and submit button.
Each node type has a coloured left bar so it is easy to tell apart at a glance.
Handles, edges, and the minimap all follow the same palette.

### Text node logic

The Text node (`src/nodes/textNode.js`) does two things:

1. **Variables.** When you type a name inside double curly braces, like
   `{{ name }}`, the node detects it with a regex and creates a matching input
   handle on its left side. Multiple variables create multiple handles, and
   duplicates are ignored.
2. **Auto-resize.** The text area grows in height to fit what you type (by
   setting its height to its scroll height), and the node grows in width based
   on the longest line, kept within a sensible range.

### Backend integration

On submit (`src/submit.js`), the frontend reads the current nodes and edges
from React Flow, sends them as form data to `POST /pipelines/parse`, and shows
the result in an alert.

The endpoint (`backend/main.py`) counts the nodes and edges and checks whether
the graph is a DAG using Kahn's algorithm: it repeatedly removes nodes that
have no incoming edges. If every node gets removed, there is no cycle. If any
are left over, they form a loop, so it is not a DAG. A node that points to
itself never loses its incoming edge, so self-loops are correctly reported as
not a DAG.

Response shape:

```
{ "num_nodes": int, "num_edges": int, "is_dag": bool }
```

## What I would do next

- Replace the alert with a proper in-app result panel.
- Add tests for the DAG check, including cycles and self-loops.
- Allow saving and reloading pipelines.
