# marimo_graph

Generate Mermaid flowcharts from Marimo notebook Python files.

This project parses Marimo cells from a `.py` notebook file, infers dependencies from function arguments and return values, and produces a Mermaid flowchart representation of the cell DAG.

## What It Does

- Detects Marimo cells decorated with `@app.cell` (and `@cell` fallback).
- Builds dependency edges from:
  - Cell input arguments (what a cell consumes)
  - Returned names (what a cell produces)
- Skips cells that contain import statements to keep the graph focused on notebook logic.
- Removes isolated cells that are not connected to any dependency edge.
- Emits Mermaid flowchart output with frontmatter config.
- Supports optional inline icon metadata in cell docstrings using:
  - `::icon:path/to/icon.svg::`

## Project Structure

- `marimo_dag_to_mermaid.py`: Main script and library functions.
- `example/test.py`: Example Marimo notebook source.
- `example/test_dag.mmd`: Example generated Mermaid output.
- `example/usage.txt`: Usage examples (CLI and in-notebook rendering).

## Requirements

- Python 3.10+ recommended (uses modern type hints).
- No external dependencies required for DAG generation.

## Installation

Clone the repository and run directly with Python.

```bash
git clone <your-repo-url>
cd marimo_graph
python marimo_dag_to_mermaid.py --help
```

## Usage

### 1) Command Line

From the project root:

```bash
python marimo_dag_to_mermaid.py example/test.py -o example/test_dag.mmd
```

If `-o` is omitted, Mermaid output is printed to stdout:

```bash
python marimo_dag_to_mermaid.py example/test.py
```

### 2) Inside a Marimo Notebook

Based on `example/usage.txt`, import and render directly:

```python
@app.cell
def _():
    import marimo as mo

    import sys
    sys.path.append('./libs')
    from marimo_dag_to_mermaid import mermaid_from_path

    return mermaid_from_path, mo

@app.cell
def _(mermaid_from_path, mo):
    mo.mermaid(mermaid_from_path(__file__))
    return
```

Note: In this repository layout, you can typically import from project root without appending `./libs`.

## API

### `mermaid_from_path(path, title="Marimo DAG") -> str`

Reads a Marimo notebook Python file and returns Mermaid diagram text.

### `parse_cells(source: str) -> list[CellInfo]`

Parses source code into structured cell metadata.

### `to_mermaid(cells, title="Marimo DAG") -> str`

Transforms parsed cells into Mermaid flowchart syntax.

## How Dependency Inference Works

For each detected cell:

- Inputs: function parameters (for example `def _(df): ...`) are treated as dependencies.
- Outputs: return values are parsed from `return ...` expressions.
- Producer mapping: a variable is linked to the latest cell that produced it.
- Edge creation: if a cell input was produced by another cell, an edge is added.

## Notes and Limitations

- Cells with imports are intentionally excluded from graph rendering.
- Only connected cells are rendered.
- Output inference is based on return statements, so cells that only display values without returning them may not contribute outputs.
- If multiple cells overwrite the same returned variable name, the latest producer is used.

## Development

Run script directly while iterating:

```bash
python marimo_dag_to_mermaid.py example/test.py
```

## License

MIT License. See `LICENSE`.
