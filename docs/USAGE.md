# Usage Guide

This document mirrors and expands the examples in `example/usage.txt`.

## CLI

Generate Mermaid from a Marimo notebook Python file:

```bash
python marimo_dag_to_mermaid.py example/test.py -o example/test_dag.mmd
```

Print to stdout instead of writing a file:

```bash
python marimo_dag_to_mermaid.py example/test.py
```

## In a Marimo Notebook

Minimal example:

```python
@app.cell
def _():
    import marimo as mo
    from marimo_dag_to_mermaid import mermaid_from_path
    return mermaid_from_path, mo

@app.cell
def _(mermaid_from_path, mo):
    mo.mermaid(mermaid_from_path(__file__))
    return
```

## Docstring Icon Support

Cell docstrings can include icon metadata:

```python
"""::icon:assets/filter.svg::Filter rows by threshold."""
```

The generated Mermaid label will include an HTML image tag for the icon.

## Graph Behavior Summary

- Import-containing cells are excluded.
- Only connected cells are rendered.
- Dependencies are inferred by matching cell inputs to previously returned names.
