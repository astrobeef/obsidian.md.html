# First-party
from collections import defaultdict
import sys
import os
import html
# Local
from pipeline import convert_markdown_to_html
from util import parse_ignore_file, should_ignore_files
from constants import (
    CONVERT_IGNORE_LIST_FILE,
    BUILT_HTML_EXTENSION,
    DEFAULT_TEMPLATE_FILE,
    DEFAULT_GLOBAL_CSS_FILE,
    DEFAULT_GLOBAL_JS_FILE)
from util import build_file_index

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

def apply_template(
        content,
        title           ="",
        template_path   =None,
        css_path        =None,
        js_path         =None
):
    template = load_template(template_path)
    if template is None:
        return content
    if "{global_css}" in template:
        if css_path:
            css_tag = f'<link rel="stylesheet" href="{css_path}">'
        else:
            raise ValueError(f"Could not get css path \"{css_path}\"")
        template = template.replace("{global_css}", css_tag)
    if "{global_js_module}" in template:
        if js_path:
            js_tag = f'<script type="module" src="{js_path}"></script>'
        else:
            raise ValueError(f"Could not get js path \"{js_path}\"")
        template = template.replace("{global_js_module}", js_tag)
    elif "{global_js}" in template:
        if js_path:
            js_tag = f'<script src="{js_path}"></script>'
        else:
            raise ValueError(f"Could not get js path \"{js_path}\"")
        template = template.replace("{global_js}", js_tag)
    return template.format(
        title=html.escape(title),
        content=content
    )

##############
# CONVERSION #
##############

def _build_relative_path(
        path        :str,
        *,
        root        :str,
        site_root   :str,
) -> str | None:
    absolute = os.path.join(site_root, path)
    return (
        os.path.relpath(absolute, root).replace("\\", "/")
        if os.path.isfile(absolute)
        else None
    )

def convert_file(
        input_path  :str,
        use_links   :bool,
        use_mathjax :bool,
        file_index  :defaultdict,
        root        :str,
        site_root   :str,
        verbose     :bool = False,
        template_path :str = DEFAULT_TEMPLATE_FILE,
) -> None:
    output_path = _convert_filename(input_path)
    with open(input_path, "r", encoding="utf-8") as f:
        text_md = f.read()
    html = convert_markdown_to_html(
        text_md,
        file_index              =file_index,
        root                    =root,
        tags_use_links          =use_links,
        embed_mathjax_scripting =use_mathjax,
        verbose                 =verbose,
    )
    title = os.path.splitext(os.path.basename(input_path))[0]
    css_rel = _build_relative_path(DEFAULT_GLOBAL_CSS_FILE, root=root, site_root=site_root)
    js_rel = _build_relative_path(DEFAULT_GLOBAL_JS_FILE, root=root, site_root=site_root)
    final_html = apply_template(html, title=title, template_path=template_path, css_path=css_rel, js_path=js_rel)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(final_html)
    print(f"Converted {input_path} -> {output_path}")
    return

def _convert_filename(input_path    :str):
    base = os.path.splitext(input_path)[0]
    filename = os.path.basename(base)
    if filename == "index":
        return os.path.join(os.path.dirname(input_path), "index.html")
    else:
        return f"{base}{BUILT_HTML_EXTENSION}"

def convert_directory(
        input_dir   :str,
        use_links   :bool,
        use_mathjax :bool,
        verbose     :bool,
        template_path :str = DEFAULT_TEMPLATE_FILE
) -> None:
    ignore_path = os.path.join(input_dir, CONVERT_IGNORE_LIST_FILE)
    ignore_patterns = parse_ignore_file(ignore_path)
    file_index = build_file_index(input_dir)
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
                convert_file(
                    input_path      = input_path,
                    use_links       = use_links,
                    use_mathjax     = use_mathjax,
                    file_index      = file_index,
                    root            = root,
                    site_root       = input_dir,
                    verbose         = verbose,
                    template_path   = template_path)
    return

###########
# CLEANUP #
###########

def clean_md_html_files(
        root            :str    =".",
        remove_index    :bool   =False,
        force           :bool   =False
):
    files_to_remove = []
    for dirpath, _, filenames in os.walk(root):
        for fname in filenames:
            if (fname.endswith(BUILT_HTML_EXTENSION)
                or (remove_index and fname.endswith("index.html"))):
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
obsidian-md-html

Usage:
    obsidian-md-html [<input.md|input_dir>] [--taglinks] [--mathjax] [--template <template.html>] [--verbose] [--help]
    obsidian-md-html --clean [--force] [--index]

Arguments:
    <input.md>       Input markdown file to convert (outputs <input>{BUILT_HTML_EXTENSION}).
    <input_dir>      Directory to recursively convert all .md files (default: current directory).
                     Outputs <file{BUILT_HTML_EXTENSION}> adjacent to each source file.
Options:
    --taglinks                  Convert tags to clickable <a> elements (for static HTML sites).
    --mathjax                   Add MathJax script for math rendering if math blocks/inlines are detected.
    --template <template.html>  Use a custom HTML template file (default: template.html).
    --verbose                   Print debug output.
    --help, -h                  Show this help message and exit.
    --clean                     Remove all built files (use "--force" or "-f" to bypass checks; use "--index" or "-i" to remove "index.html")
    --force, -f                 Neglect user double-checking during "--clean"
    --index, -i                 Remove "index.html" during "--clean"

Notes:
    - If no input is provided, the current directory is converted.
    - If a {CONVERT_IGNORE_LIST_FILE}(default:".convertignore") file is present in the input directory, listed files/directories are ignored.
    - All embedded assets are referenced, not copied.
    - Output HTML files always use the <input>{BUILT_HTML_EXTENSION}(default:".md.html") naming convention for safe cleanup.

Examples:
    obsidian-md-html                                # Convert all .md files in current directory
    obsidian-md-html notes                          # Convert all .md in 'notes' directory
    obsidian-md-html README.md                      # Convert single file (outputs README{BUILT_HTML_EXTENSION})
    obsidian-md-html --taglinks --mathjax           # Convert all .md in current directory with tag links and math
    obsidian-md-html --template mytemplate.html     # Use custom template
    obsidian-md-html --clean -f -i                  # Remove all built files immediatly, including "index.html"
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
        remove_index = '--index' in args or '-i' in args
        clean_md_html_files(force=force, remove_index=remove_index)
        sys.exit(0)
    use_links = '--taglinks' in args
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
        file_dir    = os.path.dirname(os.path.abspath(input_path))
        file_index  = build_file_index(file_dir)
        root        = file_dir
        convert_file(input_path=input_path, use_links=use_links, use_mathjax=use_mathjax, file_index=file_index, root=root, site_root=root, verbose=verbose, template_path=template_path)
if __name__ == "__main__":
    main()