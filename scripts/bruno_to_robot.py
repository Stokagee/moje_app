#!/usr/bin/env python3
"""
Bruno to Robot Framework Converter

Převede Bruno .bru soubory na Robot Framework testy.

Použití:
    python scripts/bruno_to_robot.py bruno/collections/security-learning RF/API/tests/security

Příklad výstupu:
    *** Settings ***
    Resource    common.resource
    Suite Setup    Setup API Session

    *** Test Cases ***
    Get Orders Without Token
        [Documentation]    Test that orders endpoint requires authentication
        GET    /api/v1/orders/
        Status Should Be    401
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional


def parse_bru_file(filepath: Path) -> Dict:
    """Parse .bru file and extract request details."""
    content = filepath.read_text(encoding='utf-8')

    result = {
        'name': '',
        'method': 'GET',
        'url': '',
        'headers': {},
        'body': None,
        'docstring': '',
        'vars': {}
    }

    # Extract meta name
    meta_match = re.search(r'meta\s*\{[^}]*name:\s*(.+?)[\n\s]', content)
    if meta_match:
        result['name'] = meta_match.group(1).strip()

    # Extract method
    method_match = re.search(r'method\s+(GET|POST|PUT|DELETE|PATCH)', content, re.IGNORECASE)
    if method_match:
        result['method'] = method_match.group(1).upper()

    # Also check for shorthand: get { url: ... }
    for method in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
        shorthand = re.search(rf'{method.lower()}\s*\{{\s*url:\s*(.+?)[\n\s}}]', content, re.IGNORECASE)
        if shorthand:
            result['method'] = method
            result['url'] = shorthand.group(1).strip()
            break

    # Extract URL (if not found in shorthand)
    if not result['url']:
        url_match = re.search(r'url:\s*(.+?)[\n\s]', content)
        if url_match:
            result['url'] = url_match.group(1).strip()

    # Extract headers
    headers_match = re.search(r'headers\s*\{([^}]+)\}', content, re.DOTALL)
    if headers_match:
        headers_content = headers_match.group(1)
        for line in headers_content.strip().split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                result['headers'][key.strip()] = value.strip()

    # Extract body
    body_match = re.search(r'body:json\s*\{([^}]+(?:\{[^}]*\}[^}]*)*)\}', content, re.DOTALL)
    if body_match:
        result['body'] = body_match.group(1).strip()

    # Extract docstring (comments before first block)
    doc_match = re.search(r'/\*\*\s*\n\s*\*\s*ÚKOL[^*]*\*/', content, re.DOTALL)
    if doc_match:
        # Clean up docstring
        doc = doc_match.group(0)
        doc = re.sub(r'/\*\*|\*/', '', doc)
        doc = re.sub(r'^\s*\*\s*', '', doc, flags=re.MULTILINE)
        result['docstring'] = doc.strip()

    return result


def convert_bru_to_robot(bru_data: Dict, index: int) -> str:
    """Convert parsed .bru data to Robot Framework test case."""
    # Clean up URL - replace Bruno variables with RF variables
    url = bru_data['url']
    url = re.sub(r'\{\{(\w+)\}\}', r'${\1}', url)

    # Clean up name for test case
    name = bru_data['name'] or f"Test {index}"
    # Remove numbers and dashes
    clean_name = re.sub(r'^[\d.\-_]+\s*', '', name)
    clean_name = clean_name.replace('-', ' ').replace('_', ' ').title()

    lines = []
    lines.append(f"*** Test Cases ***")
    lines.append(f"{clean_name}")
    lines.append(f"    [Documentation]    {bru_data['docstring'][:100] if bru_data['docstring'] else 'Auto-generated from Bruno'}")

    # Add headers as variables if needed
    headers = bru_data['headers']
    auth_header = headers.get('Authorization', '')

    # Method mapping
    method = bru_data['method']

    if auth_header:
        # Extract token variable
        token_match = re.search(r'\{\{(\w+)\}\}', auth_header)
        if token_match:
            token_var = token_match.group(1)
            lines.append(f"    ${{'headers'}}=    Create Dictionary    Authorization=Bearer ${{{token_var}}}")
            lines.append(f"    {method}    {url}    headers=${{headers}}")
        else:
            lines.append(f"    ${{'headers'}}=    Create Dictionary    Authorization={auth_header}")
            lines.append(f"    {method}    {url}    headers=${{headers}}")
    else:
        lines.append(f"    {method}    {url}")

    # Add body if present
    if bru_data['body']:
        body = bru_data['body']
        body = re.sub(r'\{\{(\w+)\}\}', r'${\1}', body)
        lines.append(f"    # Body: {body[:50]}...")

    lines.append("")

    return '\n'.join(lines)


def process_collection(source_dir: Path, output_dir: Path):
    """Process all .bru files in collection and generate RF tests."""
    output_dir.mkdir(parents=True, exist_ok=True)

    all_tests = []
    all_tests.append("*** Settings ***")
    all_tests.append("Resource    common.resource")
    all_tests.append("Suite Setup    Setup API Session")
    all_tests.append("")
    all_tests.append("*** Variables ***")
    all_tests.append("${base_url}           http://localhost:20300/api/v1")
    all_tests.append("${auth_url}           http://localhost:5105")
    all_tests.append("${access_token}       YOUR_TOKEN_HERE")
    all_tests.append("${csrf_token}         YOUR_CSRF_TOKEN_HERE")
    all_tests.append("")

    index = 0
    for bru_file in sorted(source_dir.rglob('*.bru')):
        # Skip folder.bru and environment files
        if bru_file.name == 'folder.bru' or bru_file.parent.name == 'environments':
            continue

        print(f"Processing: {bru_file.relative_to(source_dir)}")
        bru_data = parse_bru_file(bru_file)
        test_case = convert_bru_to_robot(bru_data, index)
        all_tests.append(test_case)
        index += 1

    # Write output
    output_file = output_dir / 'security_tests.robot'
    output_file.write_text('\n'.join(all_tests), encoding='utf-8')
    print(f"\nGenerated: {output_file}")
    print(f"Total test cases: {index}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        print("\nUsage: python bruno_to_robot.py <bruno_collection_dir> [output_dir]")
        print("\nExample:")
        print("  python scripts/bruno_to_robot.py bruno/collections/security-learning RF/API/tests/security")
        sys.exit(1)

    source_dir = Path(sys.argv[1])
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path('RF/API/tests/security')

    if not source_dir.exists():
        print(f"Error: Source directory not found: {source_dir}")
        sys.exit(1)

    process_collection(source_dir, output_dir)


if __name__ == '__main__':
    main()
