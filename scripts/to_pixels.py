#!/usr/bin/env python3
"""Convert a Modelfile.i2i Layout draft (norm1000 boxes) to a pixel draft.

Output is the "abs" / "xyxy" draft accepted by the official MOSS-Image
compile_prompt.py. Usage:

    python scripts/to_pixels.py draft.json --output pixels.json
    python scripts/to_pixels.py draft.json | python compile_prompt.py - --output prompt.txt
"""
import argparse
import json
import math
import re
import sys


def load(path):
    raw = sys.stdin.read() if path == "-" else open(path, encoding="utf-8").read()
    raw = re.sub(r"^\s*```(?:json)?\s*|\s*```\s*$", "", raw.strip())
    return json.loads(raw)


def convert(draft):
    width, height = draft.get("width"), draft.get("height")
    if not (isinstance(width, int) and isinstance(height, int) and width > 0 and height > 0):
        raise ValueError("width and height must be positive integers")
    space = draft.get("bbox_coord_space")
    if draft.get("bbox_format") != "xyxy" or space not in ("norm1000", "abs"):
        raise ValueError('expected bbox_format "xyxy" and bbox_coord_space "norm1000" or "abs"')
    if not draft.get("items"):
        raise ValueError("items must be a non-empty list")

    sx, sy = (width / 1000, height / 1000) if space == "norm1000" else (1, 1)
    for i, item in enumerate(draft["items"]):
        if item.get("label") not in ("object", "character", "text"):
            raise ValueError(f"item {i}: invalid label {item.get('label')!r}")
        if item["label"] == "text" and not item.get("text"):
            raise ValueError(f"item {i}: text item without a text field")
        x0, y0, x1, y1 = item["bbox"]
        # Floor the min edges and ceil the max edges so the box never shrinks.
        box = [math.floor(x0 * sx), math.floor(y0 * sy), math.ceil(x1 * sx), math.ceil(y1 * sy)]
        box = [min(max(box[0], 0), width), min(max(box[1], 0), height),
               min(max(box[2], 0), width), min(max(box[3], 0), height)]
        if box[0] >= box[2] or box[1] >= box[3]:
            raise ValueError(f"item {i}: empty box after conversion {box}")
        item["bbox"] = box

    draft["bbox_coord_space"] = "abs"
    return draft


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("draft", help="draft JSON file, or - for stdin")
    ap.add_argument("--output", "-o", help="write the pixel draft here instead of stdout")
    args = ap.parse_args()
    try:
        result = convert(load(args.draft))
    except (ValueError, KeyError, TypeError, json.JSONDecodeError) as e:
        sys.exit(f"error: {e}")
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        open(args.output, "w", encoding="utf-8").write(text + "\n")
    else:
        print(text)


if __name__ == "__main__":
    main()
