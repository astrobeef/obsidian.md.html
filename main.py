# First-party
import sys
import os
# Local
from pipeline import convert_markdown_to_html
from util import parse_ignore_file, should_ignore_files
from constants import CONVERT_IGNORE_LIST_FILE, BUILT_HTML_EXTENSION

def convert_file(input_path, use_links, use_mathjax, verbose):
    output_path = os.path.splitext(input_path)[0]  + BUILT_HTML_EXTENSION
    with open(input_path, "r", encoding="utf-8") as f:
        text_md = f.read()
    html = convert_markdown_to_html(
        text_md,
        tags_use_links=use_links,
        embed_mathjax_scripting=use_mathjax,
        verbose=verbose
    )
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Converted {input_path} -> {output_path}")

def convert_directory(input_dir, use_links, use_mathjax, verbose):
    ignore_path = os.path.join(input_dir, CONVERT_IGNORE_LIST_FILE)
    ignore_patterns = parse_ignore_file(ignore_path)
    for root, dirs, files in os.walk(input_dir):
        rel_dir = os.path.relpath(root, input_dir)
        dirs[:] = [d for d in dirs if not should_ignore_files(os.path.normpath(os.path.join(rel_dir, d)), ignore_patterns, is_dir=True)]
        for filename in files:
            rel_path = os.path.normpath(os.path.join(rel_dir, filename))
            if should_ignore_files(rel_path, ignore_patterns):
                continue
            if filename.lower().endswith(".md"):
                input_path = os.path.join(root, filename)
                convert_file(input_path, use_links, use_mathjax, verbose)

def print_help():
    print("""
obsidian-md-to-html

Usage:
    python main.py [<input.md|input_dir>] [--links] [--mathjax] [--verbose] [--help]

Arguments:
    <input.md>       Input markdown file to convert (outputs <input.md>.html).
    <input_dir>      Directory to recursively convert all .md files (default: current directory).
                     Outputs <file.md.html> adjacent to each source file.
Options:
    --links          Convert tags to clickable <a> elements (for static HTML sites).
    --mathjax        Add MathJax script for math rendering if math blocks/inlines are detected.
    --verbose        Print debug output.
    --help, -h       Show this help message and exit.

Notes:
    - If no input is provided, the current directory is converted.
    - If a .convertignore file (or whatever you've renamed it in constants.py) is present in the input directory, listed files/directories are ignored.
    - All embedded assets are referenced, not copied.
    - Output HTML files always use the <input>.md.html naming convention for safe cleanup.

Examples:
    python main.py                    # Convert all .md files in current directory
    python main.py notes              # Convert all .md in 'notes' directory
    python main.py README.md          # Convert single file (outputs README.md.html)
    python main.py --links --mathjax  # Convert all .md in current directory with tag links and math
""")

def main():
    args = sys.argv[1:]
    if '--help' in args or '-h' in args:
        print_help()
        sys.exit(0)
    use_links = '--links' in args
    use_mathjax = '--mathjax' in args
    verbose = '--verbose' in args
    args = [arg for arg in args if not arg.startswith('--')]
    input_path = args[0] if len(args) > 0 else "."
    if os.path.isdir(input_path):
        convert_directory(input_path, use_links, use_mathjax, verbose)
    else:
        if not input_path.lower().endswith('.md'):
            print("Error: Input file must be a markdown (.md) file.")
            sys.exit(1)
        convert_file(input_path, use_links, use_mathjax, verbose)

if __name__ == "__main__":
    main()