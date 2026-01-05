#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# USAGE: python tools/site-graph/build.py

import os
import re
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]          # repo root
CONTENT_DIR = ROOT / "content"
OUT_DIR = Path(__file__).resolve().parent / "out"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Match: {{< ref "xxx" >}}  {{< relref "xxx" >}}
REF_RE = re.compile(r'{{<\s*(ref|relref)\s+"([^"]+)"\s*>}}')

def read_front_matter_title(text: str) -> str | None:
    # Minimal: support YAML (---) or TOML (+++)
    # Return first "title:" or 'title ='
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            fm = text[3:end]
            m = re.search(r'^\s*title\s*:\s*(.+)\s*$', fm, re.MULTILINE)
            if m:
                return m.group(1).strip().strip('"').strip("'")
    if text.startswith("+++"):
        end = text.find("\n+++", 3)
        if end != -1:
            fm = text[3:end]
            m = re.search(r'^\s*title\s*=\s*(.+)\s*$', fm, re.MULTILINE)
            if m:
                return m.group(1).strip().strip('"').strip("'")
    return None

def norm_ref(s: str) -> str:
    s = s.strip().lstrip("/")
    # remove leading "content/" if someone wrote it
    if s.startswith("content/"):
        s = s[len("content/"):]
    # normalize extensions
    s = s[:-3] if s.endswith(".md") else s
    s = s[:-1] if s.endswith("/") else s
    return s

def file_keys(rel_md_path: str) -> set[str]:
    # rel_md_path like: notes/abc/index.md  or notes/abc.md
    p = rel_md_path.replace("\\", "/")
    if p.endswith(".md"):
        p_noext = p[:-3]
    else:
        p_noext = p

    keys = set()

    if p.endswith("/index.md"):
        base = p[:-len("/index.md")]
        keys |= {base, base + "/", base + "/index", base + "/index.md"}
    else:
        keys |= {p_noext, p_noext + ".md"}

    return {k.rstrip("/") for k in keys}

def node_id(key: str) -> str:
    # stable short id for mermaid node
    h = hashlib.sha1(key.encode("utf-8")).hexdigest()[:10]
    return f"N{h}"

def main():
    # 1) index all markdown files under content/
    files = []
    key_to_file = {}

    for md in CONTENT_DIR.rglob("*.md"):
        rel = md.relative_to(CONTENT_DIR).as_posix()
        files.append((md, rel))
        for k in file_keys(rel):
            key_to_file[k] = rel

    # 2) extract edges
    nodes = {}  # key -> label
    edges = set()

    for md_path, rel in files:
        text = md_path.read_text(encoding="utf-8", errors="ignore")
        src_key = norm_ref(rel[:-3])  # default key based on file path (no .md)
        # better canonical key for index.md: notes/abc/index -> notes/abc
        if rel.endswith("/index.md"):
            src_key = norm_ref(rel[:-len("/index.md")])

        title = read_front_matter_title(text)
        label = title if title else src_key.split("/")[-1]
        nodes[src_key] = label

        for _, target in REF_RE.findall(text):
            t = norm_ref(target)
            # resolve to known file key if possible
            resolved = None
            # try common variants
            candidates = [
                t,
                t + "/index",
                t + "/index.md",
                t,
            ]
            for c in candidates:
                c = norm_ref(c)
                if c in key_to_file:
                    # canonicalize index to folder base
                    if key_to_file[c].endswith("/index.md"):
                        resolved = norm_ref(key_to_file[c][:-len("/index.md")])
                    else:
                        resolved = norm_ref(key_to_file[c][:-3])
                    break
            if not resolved:
                # keep as-is (still useful for spotting broken refs)
                resolved = t

            edges.add((src_key, resolved))

    # ensure target nodes exist in nodes dict (even if unresolved)
    for _, t in edges:
        nodes.setdefault(t, t.split("/")[-1] if t else t)

    # 3) write mermaid
    out_mmd = OUT_DIR / "graph.mmd"
    with out_mmd.open("w", encoding="utf-8") as f:
        f.write("graph TD\n")
        # node declarations (stable order)
        for k in sorted(nodes.keys()):
            nid = node_id(k)
            label = nodes[k].replace('"', '\\"')
            f.write(f'  {nid}["{label}"]\n')
        f.write("\n")
        for s, t in sorted(edges):
            f.write(f"  {node_id(s)} --> {node_id(t)}\n")

    print(f"[OK] Mermaid written: {out_mmd}")

if __name__ == "__main__":
    main()
