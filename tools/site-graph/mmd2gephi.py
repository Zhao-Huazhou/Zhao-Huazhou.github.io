#!/usr/bin/env python3
# Convert a Mermaid flowchart .mmd into Gephi CSV (edges.csv + nodes.csv)
# Works best when your .mmd uses simple edges like: A --> B, A -->|label| B, A[Text] --> B

import re
from pathlib import Path

EDGE_RE = re.compile(
    r'^\s*([A-Za-z0-9_:\-\.]+)\s*([-]{1,2}\.?-?>|==?>)\s*(?:\|\s*([^|]+?)\s*\|\s*)?([A-Za-z0-9_:\-\.]+)\s*$'
)
NODE_LABEL_RE = re.compile(r'([A-Za-z0-9_:\-\.]+)\s*(?:\[\s*(.*?)\s*\]|\(\s*(.*?)\s*\)|\{\s*(.*?)\s*\})')

def parse_nodes_labels(text: str):
    labels = {}
    for m in NODE_LABEL_RE.finditer(text):
        node_id = m.group(1)
        label = next((g for g in m.groups()[1:] if g), None)
        if label:
            labels[node_id] = label
    return labels

def main():
    BASE_DIR = Path(__file__).resolve().parent
    mmd_path = BASE_DIR / "out" / "graph.mmd"
    if not mmd_path.exists():
        raise SystemExit("graph.mmd not found in current directory")

    content = mmd_path.read_text(encoding="utf-8")
    labels = parse_nodes_labels(content)

    edges = []
    nodes = set()

    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("%%") or line.startswith("flowchart") or line.startswith("graph"):
            continue
        # strip trailing semicolon
        if line.endswith(";"):
            line = line[:-1].strip()

        m = EDGE_RE.match(line)
        if not m:
            continue

        src, arrow, elabel, dst = m.groups()
        nodes.add(src); nodes.add(dst)

        # Mermaid arrows usually mean directed; treat as directed for Gephi
        edges.append((src, dst, (elabel or "").strip()))

    out_dir = BASE_DIR / "out"
    out_dir.mkdir(exist_ok=True)

    edges_csv = out_dir / "edges.csv"
    nodes_csv = out_dir / "nodes.csv"

    # write edges.csv (Gephi "Edges table" import)
    edges_csv.write_text(
        "Source,Target,Type,Label\n" +
        "\n".join(f"{s},{t},Directed,{lbl.replace(',', ' ')}" for s, t, lbl in edges),
        encoding="utf-8"
    )

    # write nodes.csv (optional but nice for labels)
    nodes_csv.write_text(
        "Id,Label\n" +
        "\n".join(f"{nid},{labels.get(nid, nid).replace(',', ' ')}" for nid in sorted(nodes)),
        encoding="utf-8"
    )

    print(f"OK: {len(nodes)} nodes, {len(edges)} edges -> nodes.csv, edges.csv")

if __name__ == "__main__":
    main()
