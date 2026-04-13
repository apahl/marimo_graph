from __future__ import annotations

import argparse
import ast
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass
class CellInfo:
    index: int
    name: str
    inputs: list[str]
    outputs: list[str]
    contains_imports: bool
    docstring: str | None


ICON_RE = re.compile(r"::icon:(.*?)::")


def is_marimo_cell(fn: ast.FunctionDef) -> bool:
    for dec in fn.decorator_list:
        # @app.cell
        if isinstance(dec, ast.Attribute) and dec.attr == "cell":
            return True
        # @cell (less common)
        if isinstance(dec, ast.Name) and dec.id == "cell":
            return True
    return False


def cell_contains_imports(fn: ast.FunctionDef) -> bool:
    return any(isinstance(n, (ast.Import, ast.ImportFrom)) for n in ast.walk(fn))


def extract_names_from_return_value(node: ast.AST | None) -> list[str]:
    if node is None:
        return []

    if isinstance(node, ast.Name):
        return [node.id]

    if isinstance(node, (ast.Tuple, ast.List)):
        names: list[str] = []
        for elt in node.elts:
            names.extend(extract_names_from_return_value(elt))
        return names

    # Fallback: expression text (Python 3.9+)
    try:
        return [ast.unparse(node)]
    except Exception:
        return ["<expr>"]


def extract_return_names(fn: ast.FunctionDef) -> list[str]:
    names: list[str] = []
    for n in ast.walk(fn):
        if isinstance(n, ast.Return):
            names.extend(extract_names_from_return_value(n.value))

    # preserve order + dedupe
    seen: set[str] = set()
    ordered: list[str] = []
    for n in names:
        if n not in seen:
            seen.add(n)
            ordered.append(n)
    return ordered


def parse_cells(source: str) -> list[CellInfo]:
    tree = ast.parse(source)
    cells: list[CellInfo] = []
    idx = 1

    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and is_marimo_cell(node):
            inputs = [a.arg for a in node.args.args]
            outputs = extract_return_names(node)
            doc = ast.get_docstring(node, clean=True)
            cells.append(
                CellInfo(
                    index=idx,
                    name=node.name,
                    inputs=inputs,
                    outputs=outputs,
                    contains_imports=cell_contains_imports(node),
                    docstring=doc,
                )
            )
            idx += 1

    return cells


def node_id(prefix: str, raw: str) -> str:
    cleaned = "".join(ch if ch.isalnum() else "_" for ch in raw)
    if not cleaned:
        cleaned = "empty"
    return f"{prefix}_{cleaned}"


def quote_label(s: str) -> str:
    return s.replace('"', '\\"')


def to_mermaid(cells: Iterable[CellInfo], title: str = "Marimo DAG") -> str:
    # remove import-containing cells from the graph
    cell_list = [c for c in cells if not c.contains_imports]

    # build producer map and cell-to-cell edges first
    producer_for_var: dict[str, int] = {}
    edges: set[tuple[int, int]] = set()

    for c in cell_list:
        for v in c.inputs:
            src = producer_for_var.get(v)
            if src is not None and src != c.index:
                edges.add((src, c.index))

        for v in c.outputs:
            producer_for_var[v] = c.index

    # keep only connected cells (appear in at least one edge)
    connected_ids = {i for edge in edges for i in edge}
    connected_cells = [c for c in cell_list if c.index in connected_ids]

    lines: list[str] = []
    lines.append("---")
    lines.append("config:")
    lines.append(f'  title: "{quote_label(title)}"')
    lines.append("  look: handdrawn")  # classic or handdrawn
    lines.append("  theme: neutral")  # default, dark, forest, or neutral
    lines.append("  flowchart:")
    lines.append("    curve: basis") # basis, natural
    lines.append("---")
    lines.append("flowchart LR")

    # cell nodes (connected only)
    for c in connected_cells:
        cid = f"cell_{c.index}"
        base = f"<b>Cell {c.index}</b>" if c.name == "_" else f"<b>{c.name}</b>"

        icon_path, clean_doc = split_docstring_icon(c.docstring)
        icon_html = f'<img src="{icon_path}" height="16"/>&nbsp;' if icon_path else ""

        if clean_doc:
            doc = clean_doc.replace("\n", "<br/>")
            label = f"{icon_html}{base}<br/>{doc}"
        else:
            label = f"{icon_html}{base}"

        lines.append(f'    {cid}["{quote_label(label)}"]')

    # render edges
    for src, dst in sorted(edges):
        lines.append(f"    cell_{src} ==> cell_{dst}")

    return "\n".join(lines) + "\n"


def split_docstring_icon(docstring: str | None) -> tuple[str | None, str | None]:
    """Return (icon_path, cleaned_docstring)."""
    if not docstring:
        return None, None

    m = ICON_RE.search(docstring)
    icon_path = m.group(1).strip() if m else None

    cleaned = ICON_RE.sub("", docstring).strip()
    return icon_path, (cleaned or None)


def mermaid_from_path(path: str | Path, title: str = "Marimo DAG") -> str:
    in_path = Path(path)
    source = in_path.read_text(encoding="utf-8")
    cells = parse_cells(source)
    return to_mermaid(cells, title=title)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a Mermaid DAG from a Marimo notebook .py file."
    )
    parser.add_argument(
        "input",
        nargs="?",
        default="test_2.py",
        help="Path to Marimo notebook Python file (default: test_2.py)",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="Write Mermaid output to file (default: print to stdout)",
    )
    args = parser.parse_args()

    in_path = Path(args.input)
    source = in_path.read_text(encoding="utf-8")
    cells = parse_cells(source)

    mermaid = to_mermaid(cells, title=f"Marimo DAG: {in_path.name}")

    if args.output:
        Path(args.output).write_text(mermaid, encoding="utf-8")
        print(f"Wrote Mermaid diagram to: {args.output}")
    else:
        print(mermaid)


if __name__ == "__main__":
    main()
