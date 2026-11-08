#!/usr/bin/env python3
"""Compute uniform-grid sprite rects for a sheet and emit them for Unity.

Why this exists: slicing a sheet by hand in the Sprite Editor is fine once, and
miserable for a set. Unity's official /unity:sprite-editor skill owns the
interactive and irregular cases; this script covers the common uniform grid and
produces something the Editor can apply deterministically.

Stdlib only — PNG dimensions are read straight from the IHDR chunk, so there is
no Pillow dependency.

Usage
  python3 scripts/slice-spritesheet.py SHEET.png --cols 8 --rows 4 [options]
  python3 scripts/slice-spritesheet.py SHEET.png --cell 32x32 [options]

Options
  --cell WxH         Cell size in pixels (alternative to --cols/--rows)
  --cols N --rows N  Grid counts
  --pivot NAME       bottom-center (default), center, bottom-left, top-left, custom
  --pivot-xy X,Y     Normalised pivot when --pivot custom
  --padding N        Pixels of padding between cells (default 0)
  --offset X,Y       Pixels skipped at the left/top before the first cell
  --name PREFIX      Sprite name prefix (default: the file stem)
  --format json|csharp   Output shape (default json)

Unity's sprite rects are measured from the BOTTOM-LEFT of the texture, while
sheets are authored top-left-first. Row 0 here is the TOP row, and the emitted
y is converted for you — getting this backwards is the usual reason a sliced
animation plays in the wrong order.
"""
from __future__ import annotations

import argparse
import json
import os
import struct
import sys

PIVOTS = {
    "bottom-center": (0.5, 0.0),
    "center": (0.5, 0.5),
    "bottom-left": (0.0, 0.0),
    "top-left": (0.0, 1.0),
}


def png_size(path: str) -> tuple[int, int]:
    """Read width and height from a PNG's IHDR chunk."""
    with open(path, "rb") as handle:
        signature = handle.read(8)
        if signature != b"\x89PNG\r\n\x1a\n":
            raise SystemExit(f"{path}: not a PNG. Convert it first, or pass --cell with explicit counts.")
        handle.read(4)  # IHDR length
        if handle.read(4) != b"IHDR":
            raise SystemExit(f"{path}: malformed PNG, no IHDR chunk")
        width, height = struct.unpack(">II", handle.read(8))
    return width, height


def parse_pair(value: str, flag: str) -> tuple[int, int]:
    separator = "x" if "x" in value else ","
    try:
        first, second = value.split(separator)
        return int(first), int(second)
    except ValueError:
        raise SystemExit(f"{flag}: expected two numbers like 32x32 or 32,32, got {value!r}")


def main() -> int:
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument("sheet")
    parser.add_argument("--cell")
    parser.add_argument("--cols", type=int)
    parser.add_argument("--rows", type=int)
    parser.add_argument("--pivot", default="bottom-center")
    parser.add_argument("--pivot-xy")
    parser.add_argument("--padding", type=int, default=0)
    parser.add_argument("--offset", default="0,0")
    parser.add_argument("--name")
    parser.add_argument("--format", default="json", choices=["json", "csharp"])
    args = parser.parse_args()

    if not os.path.exists(args.sheet):
        raise SystemExit(f"{args.sheet}: no such file")

    sheet_width, sheet_height = png_size(args.sheet)
    offset_x, offset_y = parse_pair(args.offset, "--offset")
    pad = args.padding

    if args.cell:
        cell_width, cell_height = parse_pair(args.cell, "--cell")
        cols = (sheet_width - offset_x + pad) // (cell_width + pad)
        rows = (sheet_height - offset_y + pad) // (cell_height + pad)
    elif args.cols and args.rows:
        cols, rows = args.cols, args.rows
        cell_width = (sheet_width - offset_x - pad * (cols - 1)) // cols
        cell_height = (sheet_height - offset_y - pad * (rows - 1)) // rows
    else:
        raise SystemExit("pass either --cell WxH or both --cols and --rows")

    if cols < 1 or rows < 1 or cell_width < 1 or cell_height < 1:
        raise SystemExit(f"grid does not fit: sheet is {sheet_width}x{sheet_height}, computed "
                         f"{cols}x{rows} cells of {cell_width}x{cell_height}")

    # A grid that does not divide the sheet exactly means the sheet, the cell
    # size, or the padding is wrong. Slicing anyway produces sprites with a
    # row of neighbouring pixels baked in, which is very hard to spot later.
    used_width = offset_x + cols * cell_width + pad * (cols - 1)
    used_height = offset_y + rows * cell_height + pad * (rows - 1)
    if used_width != sheet_width or used_height != sheet_height:
        print(f"warning: grid covers {used_width}x{used_height} of a {sheet_width}x{sheet_height} sheet. "
              f"{sheet_width - used_width}px right and {sheet_height - used_height}px bottom are unused — "
              "check --cell, --padding and --offset before applying.", file=sys.stderr)

    if args.pivot == "custom":
        if not args.pivot_xy:
            raise SystemExit("--pivot custom requires --pivot-xy X,Y")
        pivot_x, pivot_y = (float(v) for v in args.pivot_xy.split(","))
    elif args.pivot in PIVOTS:
        pivot_x, pivot_y = PIVOTS[args.pivot]
    else:
        raise SystemExit(f"--pivot: expected one of {sorted(PIVOTS)} or 'custom', got {args.pivot!r}")

    prefix = args.name or os.path.splitext(os.path.basename(args.sheet))[0]

    # Unity addresses assets by a path relative to the project root, starting
    # with "Assets/". Emitting anything else produces C# that silently returns a
    # null importer, so say so rather than letting it fail inside the Editor.
    normalised = args.sheet.replace(os.sep, "/")
    marker = normalised.find("Assets/")
    if marker == -1:
        asset_path = normalised
        print(f"warning: {args.sheet} is not inside an Assets/ folder, so the emitted path is not one "
              "Unity can resolve. Move the sheet into the project before applying the C# output.",
              file=sys.stderr)
    else:
        asset_path = normalised[marker:]

    rects = []
    for row in range(rows):              # row 0 is the TOP row of the sheet
        for col in range(cols):
            x = offset_x + col * (cell_width + pad)
            top = offset_y + row * (cell_height + pad)
            y = sheet_height - top - cell_height   # convert to Unity's bottom-left origin
            rects.append({
                "name": f"{prefix}_{row * cols + col}",
                "x": x, "y": y, "width": cell_width, "height": cell_height,
                "pivotX": pivot_x, "pivotY": pivot_y,
            })

    if args.format == "json":
        print(json.dumps({
            "sheet": asset_path,
            "sheetWidth": sheet_width, "sheetHeight": sheet_height,
            "columns": cols, "rows": rows,
            "cellWidth": cell_width, "cellHeight": cell_height,
            "spriteCount": len(rects),
            "rects": rects,
        }, indent=2))
    else:
        # A statement block for `script eval`: no using directives, fully
        # qualified types, and a returned value that lands at data.result.result.
        print(f"// Apply {len(rects)} sprite rects to {asset_path}")
        print(f'var importer = (UnityEditor.TextureImporter)UnityEditor.AssetImporter.GetAtPath('
              f'"{asset_path}");')
        print("importer.spriteImportMode = UnityEditor.SpriteImportMode.Multiple;")
        print("var sheet = new System.Collections.Generic.List<UnityEditor.SpriteMetaData>();")
        for rect in rects:
            print(f'sheet.Add(new UnityEditor.SpriteMetaData {{ name = "{rect["name"]}", '
                  f'rect = new UnityEngine.Rect({rect["x"]}f, {rect["y"]}f, {rect["width"]}f, {rect["height"]}f), '
                  f'alignment = (int)UnityEngine.SpriteAlignment.Custom, '
                  f'pivot = new UnityEngine.Vector2({rect["pivotX"]}f, {rect["pivotY"]}f) }});')
        print("importer.spritesheet = sheet.ToArray();")
        print("UnityEditor.EditorUtility.SetDirty(importer);")
        print("importer.SaveAndReimport();")
        print(f"return {len(rects)};")
    return 0


if __name__ == "__main__":
    sys.exit(main())
