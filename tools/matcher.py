#!/usr/bin/env python3
"""
Simple PoC matcher: compares two AST/example JSON files and computes
cosine similarity between provided embedding vectors (if present).

Usage: python tools/matcher.py examples/sample_theme.json examples/sample_filmdna.json
"""
import sys
import json
import math
from typing import List


def load_json(path: str):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def extract_embedding(data) -> List[float]:
    # Try common locations
    if isinstance(data, dict):
        if 'embeddings' in data and isinstance(data['embeddings'], list):
            return [float(x) for x in data['embeddings']]
        # FilmDNA / theme files may not have embeddings. fallback to features
        if 'emotion_curve' in data:
            # simple hand-rolled vector from emotion counts (PoC)
            vec = []
            for k, v in sorted(data['emotion_curve'].items()):
                vec.append(float(len(str(v))))
            return vec
        if 'features' in data:
            f = data['features']
            if 'mfcc' in f:
                return [float(x) for x in f['mfcc']]
    return []


def cosine(a: List[float], b: List[float]) -> float:
    if not a or not b:
        return 0.0
    # pad to same length
    n = max(len(a), len(b))
    a = a + [0.0] * (n - len(a))
    b = b + [0.0] * (n - len(b))
    dot = sum(x*y for x,y in zip(a,b))
    na = math.sqrt(sum(x*x for x in a))
    nb = math.sqrt(sum(y*y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def main():
    if len(sys.argv) < 3:
        print("Usage: matcher.py <path_a.json> <path_b.json>")
        sys.exit(1)
    a = load_json(sys.argv[1])
    b = load_json(sys.argv[2])
    va = extract_embedding(a)
    vb = extract_embedding(b)
    score = cosine(va, vb)
    print(f"Cosine similarity: {score:.4f}")

if __name__ == '__main__':
    main()
