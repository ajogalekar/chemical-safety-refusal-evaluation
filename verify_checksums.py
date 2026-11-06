#!/usr/bin/env python3
"""Verify the prepared archive before running analyses or editing files."""
from pathlib import Path
import hashlib

root=Path(__file__).resolve().parent
lines=(root/'CHECKSUMS.sha256').read_text().splitlines()
for line in lines:
    expected,name=line.split('  ',1)
    path=root/name
    assert path.is_file(),f'Missing file: {name}'
    actual=hashlib.sha256(path.read_bytes()).hexdigest()
    assert actual==expected,f'Checksum mismatch: {name}'
print(f'All {len(lines)} file checksums match.')
