# Third-party
import markdown as md
# First-party
from os import path
from html import unescape

PREVIEW_LENGTH = 512#characters

##############
# CONVERSION #
##############

def _convert_md_to_html(
        text_md :str,
        verbose :bool = False,
):
    text_html = md.markdown(text_md)
    if verbose:
        print(f"------TO HTML------\n{text_html[:min(len(text_html), PREVIEW_LENGTH)]}{"..." if len(text_html) > PREVIEW_LENGTH else ""}\n-----END OF HTML-----")
    return text_html

#######
# I/O #
#######

def _read_md(
        path    :str,
        verbose :bool = False,
) -> str:
    # In context, a file should never be called to open if it doesn't exist, so neglecting validation
    with open(path, "r", encoding="utf-8") as f:
        text_md = f.read()
        if verbose:
            print(f"-----{path}-----\n{text_md[:min(len(text_md), PREVIEW_LENGTH)]}{"..." if len(text_md) > PREVIEW_LENGTH else ""}...\n-----END OF MD-----")
        return text_md

def _path_md_to_html(
        path_md :str,
        verbose :bool = False
) -> str:
    base, _ = path.splitext(path_md)
    path_html = f"{base}.html"
    if verbose:
        print(f"Converted md_path \"{path_md}\" to \"{path_html}\"")
    return path_html

def _save_html(
        path_md :str,
        html    :str,
        verbose :bool = False
) -> str:
    path_html = _path_md_to_html(path_md)
    with open(path_html, "w", encoding="utf-8") as f:
        f.write(html)
        if verbose:
            print(f"Saved \"{path_md}\" as HTML to \"{path_html}\"")
    return

test_md = _read_md("README.md", True)
test_html = _convert_md_to_html(test_md, True)
_save_html("README.md", test_html, True)