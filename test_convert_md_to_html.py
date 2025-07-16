# Third-party
import markdown as md
# First-party
from urllib.parse import quote
from os import path
import re

PREVIEW_LENGTH = 512#characters

##############
# CONVERSION #
##############

def _convert_md_to_html(
        text_md :str,
        verbose :bool = False,
):
    text_md = _replace_wikilinks(text_md, verbose=verbose)
    text_md = _smart_insert_spacing(text_md)
    text_html = md.markdown(text_md)
    if verbose:
        print(f"------TO HTML------\n{text_html[:min(len(text_html), PREVIEW_LENGTH)]}{"..." if len(text_html) > PREVIEW_LENGTH else ""}\n-----END OF HTML-----")
    return text_html

def _replace_wikilinks(
        text_md :str,
        verbose :bool = False
) -> str:
    def i_replace(match):
        inner = match.group(1)
        if "|" in inner:
            target, display = inner.split("|", 1)
        else:
            target, display = inner, inner
        href = _path_md_to_html(target, verbose=verbose)
        html = f'<a href="{href}">{display.strip()}</a>'
        if verbose:
            print(f"Converted wikilink \"{inner}\" to \"{html}\"")
        return html
    # regex to find all wikilinks [[<anything>]]
    return re.sub(r"\[\[([^\[\]]+)\]\]", i_replace, text_md)

def _smart_insert_spacing(
        text_md :str
) -> str:
    """Obsidian is smarter with markdown styling than traditional markdown displayers. For example, a list in markdown traditionally requires a space prior to note that it's a list. But Obsidian is smart enough to know it's a list and will display it as such."""
    list_pattern = re.compile(
        r"([^\n])\n(\s*(?:\d+\.\s+|\-\s+|\*\s+|\-\s*\[.\]\s+|\*\s*\[.\]\s+))"
    )
    text_md = list_pattern.sub(r"\1\n\n\2", text_md)
    heading_pattern = re.compile(r"([^\n])\n(\s*#{1,6}\s+)")
    text_md = heading_pattern.sub(r"\1\n\n\2", text_md)
    return text_md

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
    base_encoded = quote(base, safe="/")
    path_html = f"{base_encoded}.html"
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

test_file = "test.md"
test_md = _read_md(test_file, True)
test_html = _convert_md_to_html(test_md, True)
_save_html(test_file, test_html, True)