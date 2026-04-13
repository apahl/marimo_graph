import marimo

__generated_with = "0.22.5"
app = marimo.App(width="medium", auto_download=["html"])


@app.cell
def _():
    import marimo as mo
    import pandas as pd

    import sys
    sys.path.append('./libs')
    from marimo_dag_to_mermaid import mermaid_from_path

    return mermaid_from_path, mo, pd


@app.cell
def _(pd):
    """Define the dataframe"""
    df = pd.DataFrame({
        'A': [1, 2, 3],
        'B': [4, 5, 6],
        'C': [7, 8, 10]
    })
    return (df,)


@app.cell
def filter_dataframe(df):
    """Filter the dataframe"""
    df2 = df[df['A'] > 1].copy()
    df2
    return (df2,)


@app.cell
def sort(df):
    """Sort the values"""
    df3 = df.sort_values(by='B', ascending=False).copy()
    df3
    return (df3,)


@app.cell
def _(df2, df3, pd):
    """Concatenate everything"""
    df4 = pd.concat([df2, df3], ignore_index=True)
    df4
    return


@app.cell
def _(mermaid_from_path, mo):
    mo.mermaid(mermaid_from_path(__file__))
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
