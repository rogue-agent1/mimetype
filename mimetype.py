#!/usr/bin/env python3
"""mimetype - MIME type lookup and file type detection.

Single-file, zero-dependency CLI.
"""

import sys
import argparse
import mimetypes
import os

# Extra mappings not always in mimetypes
EXTRA = {
    ".md": "text/markdown", ".yaml": "application/yaml", ".yml": "application/yaml",
    ".toml": "application/toml", ".rs": "text/x-rust", ".go": "text/x-go",
    ".ts": "text/typescript", ".tsx": "text/typescript-jsx", ".jsx": "text/javascript-jsx",
    ".vue": "text/x-vue", ".svelte": "text/x-svelte", ".wasm": "application/wasm",
    ".webp": "image/webp", ".avif": "image/avif", ".heic": "image/heic",
    ".m4a": "audio/mp4", ".flac": "audio/flac", ".opus": "audio/opus",
    ".mkv": "video/x-matroska", ".webm": "video/webm",
    ".jsonl": "application/jsonl", ".ndjson": "application/x-ndjson",
    ".dockerfile": "text/x-dockerfile", ".tf": "text/x-terraform",
}

SIGNATURES = [
    (b"\x89PNG\r\n\x1a\n", "image/png"),
    (b"\xff\xd8\xff", "image/jpeg"),
    (b"GIF87a", "image/gif"), (b"GIF89a", "image/gif"),
    (b"RIFF", "audio/wav"),  # could be webp too
    (b"PK\x03\x04", "application/zip"),
    (b"\x1f\x8b", "application/gzip"),
    (b"%PDF", "application/pdf"),
    (b"\x7fELF", "application/x-elf"),
    (b"\xfe\xed\xfa", "application/x-mach-binary"),
    (b"\xcf\xfa\xed\xfe", "application/x-mach-binary"),
]


def detect_by_magic(path):
    try:
        with open(path, "rb") as f:
            header = f.read(16)
        for sig, mime in SIGNATURES:
            if header.startswith(sig):
                return mime
    except (IOError, PermissionError):
        pass
    return None


def cmd_lookup(args):
    for name in args.files:
        ext = os.path.splitext(name)[1].lower()
        mime = EXTRA.get(ext) or mimetypes.guess_type(name)[0]
        if os.path.isfile(name):
            magic = detect_by_magic(name)
            if magic and not mime:
                mime = magic
            elif magic and mime and magic != mime:
                mime = f"{mime} (magic: {magic})"
        print(f"  {name:30s}  {mime or 'unknown'}")


def cmd_ext(args):
    """Find extensions for a MIME type."""
    mime = args.mime
    exts = mimetypes.guess_all_extensions(mime)
    extra_exts = [e for e, m in EXTRA.items() if m == mime]
    all_exts = sorted(set(exts + extra_exts))
    if all_exts:
        print(f"  {mime}: {', '.join(all_exts)}")
    else:
        print(f"  No extensions for: {mime}")


def cmd_search(args):
    query = args.query.lower()
    mimetypes.init()
    found = set()
    for ext, mime in {**mimetypes.types_map, **EXTRA}.items():
        if query in mime.lower() or query in ext.lower():
            found.add((ext, mime))
    for ext, mime in sorted(found):
        print(f"  {ext:10s}  {mime}")
    if not found:
        print(f"  No matches for '{query}'")


def main():
    p = argparse.ArgumentParser(prog="mimetype", description="MIME type lookup and detection")
    sub = p.add_subparsers(dest="cmd")
    s = sub.add_parser("lookup", aliases=["l"], help="Detect MIME type of files")
    s.add_argument("files", nargs="+")
    s = sub.add_parser("ext", help="Extensions for MIME type")
    s.add_argument("mime")
    s = sub.add_parser("search", aliases=["s"], help="Search MIME types")
    s.add_argument("query")
    args = p.parse_args()
    if not args.cmd: p.print_help(); return 1
    cmds = {"lookup": cmd_lookup, "l": cmd_lookup, "ext": cmd_ext, "search": cmd_search, "s": cmd_search}
    return cmds[args.cmd](args) or 0


if __name__ == "__main__":
    sys.exit(main())
