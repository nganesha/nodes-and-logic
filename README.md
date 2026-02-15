# Nodes & Logic

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://nodes-and-logic-f95zsj3qureecfytq3ulcw.streamlit.app/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Interactive Python **Code-to-Architecture Visualizer** built with Streamlit. Paste Python code, generate a live node-link architecture map, and get LLM-powered architectural insights.

## Overview

Nodes & Logic analyzes Python source using the built-in `ast` module to detect:
- Classes
- Functions (including class methods)
- Call relationships

It then renders an interactive graph and summarizes architecture patterns using LiteLLM with support for:
- OpenAI
- Anthropic
- Ollama (local)

## Features

- Professional Streamlit UI with two-panel workflow
- Interactive architecture graph via `streamlit-agraph`
- Color-coded nodes:
  - Class nodes: blue accent
  - Function nodes: red
- Full-width, collapsible **Dashboard & LLM Insights** panel
- Real-time status indicator:
  - Pulsating dot while analysis is running
  - Solid green dot when complete
- Sidebar model/provider controls
- Local LLM support with Ollama base URL + model selection
- Graceful syntax error handling for invalid/incomplete code

## Tech Stack

- **Frontend:** Streamlit
- **Graph Visualization:** streamlit-agraph
- **Static Analysis:** Python `ast`
- **LLM Abstraction:** LiteLLM

## Project Structure

```text
.
├── app.py             # Streamlit app UI and interaction flow
├── analyzer.py        # AST extraction + LiteLLM insight generation
├── requirements.txt   # Python dependencies
└── start_app.sh       # Startup script for local run
```

## Getting Started

### 1. Clone and enter the project

```bash
git clone <your-repo-url>
cd nodes-and-logic
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the app

Option A:
```bash
./start_app.sh
```

Option B:
```bash
streamlit run app.py
```

Open the URL shown in terminal (typically `http://127.0.0.1:8501`).

## LLM Configuration

Use the sidebar to select provider and model.

### OpenAI
- Provider: `OpenAI`
- Add OpenAI API key
- Example model: `gpt-4o`

### Anthropic
- Provider: `Anthropic`
- Add Anthropic API key
- Example model: `claude-3-5-sonnet`

### Ollama (Local)
- Provider: `Ollama (Local)`
- Default model: `llama3.1:8b-instruct-q4_K_M`
- Default base URL: `http://localhost:11434`

If needed, pull/run your Ollama model first.

## How It Works

1. Paste Python code into the editor.
2. Click **Analyze Architecture**.
3. The app parses code with `ast` and builds graph nodes/edges.
4. The app requests an LLM summary for architectural insight.
5. Results are displayed as:
   - Interactive graph
   - Dashboard metrics (Classes, Functions, Links)
   - LLM insight panel

## Example Snippet

```python
class UserService:
    def create_user(self):
        self.validate()
        save_user()

    def validate(self):
        print("valid")


def save_user():
    notify()


def notify():
    print("done")
```

## Troubleshooting

- **Permission denied when starting script**
  - Run: `chmod +x start_app.sh`
  - Then: `./start_app.sh`

- **Port bind or operation not permitted**
  - Try another port:
    ```bash
    PORT=8502 ./start_app.sh
    ```

- **No LLM insight returned**
  - Verify API key (OpenAI/Anthropic)
  - For Ollama, verify server is running at configured base URL

- **Syntax error message after Analyze**
  - Fix incomplete/invalid Python code and re-run.

## Roadmap Ideas

- Export graph as JSON/PNG
- Multi-file repository analysis
- Architecture anti-pattern detection
- Diff view between code versions

## License

Add your preferred license (MIT/Apache-2.0/etc.) in a `LICENSE` file.
