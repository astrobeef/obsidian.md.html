# First-party
import sys
import os
# Local
from pipeline import convert_markdown_to_html
from util import parse_ignore_file, should_ignore_files

def convert_file(input_path, output_path, use_links, use_mathjax, verbose):
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
    ignore_path = os.path.join(input_dir, ".convertignore")
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
                out_dir = os.path.join(input_dir, os.path.dirname(rel_path))
                os.makedirs(out_dir, exist_ok=True)
                out_file = os.path.splitext(os.path.basename(filename))[0] + ".html"
                output_path = os.path.join(out_dir, out_file)
                convert_file(input_path, output_path, use_links, use_mathjax, verbose)

def main():
    args = sys.argv[1:]
    use_links = '--links' in args
    use_mathjax = '--mathjax' in args
    verbose = '--verbose' in args
    args = [arg for arg in args if not arg.startswith('--')]
    if len(args) < 1:
        print("Usage: python main.py <input.md|input_dir> [<output.html>] [--links] [--mathjax] [--verbose]")
        sys.exit(1)
    input_path = args[0]
    if os.path.isdir(input_path):
        convert_directory(input_path, use_links, use_mathjax, verbose)
    else:
        if len(args) < 2:
            print("Usage: python main.py <input.md> <output.html> [--links] [--mathjax] [--verbose]")
            sys.exit(1)
        output_path = args[1]
        convert_file(input_path, output_path, use_links, use_mathjax, verbose)

if __name__ == "__main__":
    main()