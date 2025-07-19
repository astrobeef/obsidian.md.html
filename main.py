# First-party
import sys
import os
import html
# Local
from pipeline import convert_markdown_to_html
from util import parse_ignore_file, should_ignore_files
from constants import CONVERT_IGNORE_LIST_FILE, BUILT_HTML_EXTENSION, DEFAULT_TEMPLATE_FILE

############
# TEMPLATE #
############

def load_template(path=None):
    if path and os.path.isfile(path):
        with open(path, encoding="utf-8") as f:
            return f.read()
    elif os.path.isfile("template.html"):
        with open("template.html", encoding="utf-8") as f:
            return f.read()
    else:
        return None

def apply_template(content, title="", template_path=None):
    template = load_template(template_path)
    if template is None:
        return content
    return template.format(
        title=html.escape(title),
        content=content
    )

##############
# CONVERSION #
##############

def convert_file(
        input_path  :str,
        use_links   :bool,
        use_mathjax :bool,
        verbose     :bool,
        template_path :str = DEFAULT_TEMPLATE_FILE
) -> None:
    output_path = os.path.splitext(input_path)[0]  + BUILT_HTML_EXTENSION
    with open(input_path, "r", encoding="utf-8") as f:
        text_md = f.read()
    html = convert_markdown_to_html(
        text_md,
        tags_use_links          =use_links,
        embed_mathjax_scripting =use_mathjax,
        verbose                 =verbose
    )
    title = os.path.splitext(os.path.basename(input_path))[0]
    final_html = apply_template(html, title=title, template_path=template_path)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(final_html)
    print(f"Converted {input_path} -> {output_path}")
    return

def convert_directory(
        input_dir   :str,
        use_links   :bool,
        use_mathjax :bool,
        verbose     :bool,
        template_path :str = DEFAULT_TEMPLATE_FILE
) -> None:
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
                convert_file(input_path, use_links, use_mathjax, verbose, template_path)
    return

###########
# CLEANUP #
###########

def clean_md_html_files(
        root    :str    =".",
        force   :bool   =False
):
    files_to_remove = []
    for dirpath, _, filenames in os.walk(root):
        for fname in filenames:
            if fname.endswith(BUILT_HTML_EXTENSION):
                fpath = os.path.join(dirpath, fname)
                files_to_remove.append(fpath)
    if not files_to_remove:
        print(f"No {BUILT_HTML_EXTENSION} files found. If this is unexpected, it may be due to modification of `constants.BUILT_HTML_EXTENSION`.")
        return
    print(f"Found {len(files_to_remove)} {BUILT_HTML_EXTENSION} files to delete.")
    for fpath in files_to_remove:
        if not force:
            resp = input(f"Delete {fpath}? [y/N] ").strip().lower()
            if resp != "y":
                print("Skipped.")
                continue
        try:
            os.remove(fpath)
            print(f"Deleted {fpath}")
        except Exception as e:
            print(f"Could not delete {fpath}: {e}")

##############
# PRINT HELP #
##############

def print_help():
    print(f"""
obsidian-md-to-html

Usage:
    python main.py [<input.md|input_dir>] [--links] [--mathjax] [--template <template.html>] [--verbose] [--help]

Arguments:
    <input.md>       Input markdown file to convert (outputs <input>{BUILT_HTML_EXTENSION}).
    <input_dir>      Directory to recursively convert all .md files (default: current directory).
                     Outputs <file{BUILT_HTML_EXTENSION}> adjacent to each source file.
Options:
    --links                     Convert tags to clickable <a> elements (for static HTML sites).
    --mathjax                   Add MathJax script for math rendering if math blocks/inlines are detected.
    --template <template.html>  Use a custom HTML template file (default: template.html).
    --verbose                   Print debug output.
    --help, -h                  Show this help message and exit.

Notes:
    - If no input is provided, the current directory is converted.
    - If a {CONVERT_IGNORE_LIST_FILE}(default:".convertignore") file is present in the input directory, listed files/directories are ignored.
    - All embedded assets are referenced, not copied.
    - Output HTML files always use the <input>{BUILT_HTML_EXTENSION}(default:".md.html") naming convention for safe cleanup.

Examples:
    python main.py                              # Convert all .md files in current directory
    python main.py notes                        # Convert all .md in 'notes' directory
    python main.py README.md                    # Convert single file (outputs README{BUILT_HTML_EXTENSION})
    python main.py --links --mathjax            # Convert all .md in current directory with tag links and math
    python main.py --template mytemplate.html   # Use custom template
""")

########
# MAIN #
########

def main():
    args = sys.argv[1:]
    if '--help' in args or '-h' in args:
        print_help()
        sys.exit(0)
    if '--clean' in args:
        force = '--force' in args or '-f' in args
        clean_md_html_files(force=force)
        sys.exit(0)
    use_links = '--links' in args
    use_mathjax = '--mathjax' in args
    verbose = '--verbose' in args
    template_path = DEFAULT_TEMPLATE_FILE
    if '--template' in args:
        t_idx = args.index('--template')
        if t_idx < len(args) - 1:
            template_path = args[t_idx + 1]
            del args[t_idx:t_idx+2]
        else:
            print("Error: --template flag requires a path to the template HTML file.")
            sys.exit(1)
    args = [arg for arg in args if not arg.startswith('--')]
    input_path = args[0] if len(args) > 0 else "."
    if os.path.isdir(input_path):
        convert_directory(input_path, use_links, use_mathjax, verbose, template_path)
    else:
        if not input_path.lower().endswith('.md'):
            print("Error: Input file must be a markdown (.md) file.")
            sys.exit(1)
        convert_file(input_path, use_links, use_mathjax, verbose, template_path)

if __name__ == "__main__":
    main()