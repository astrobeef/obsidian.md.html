# Third-party
import markdown as md
from markdown.extensions.toc import TocExtension as tocExt
from bs4 import BeautifulSoup as BS
# First-party
from urllib.parse import quote
from os import path
import re

PREVIEW_LENGTH = 512#characters

# Classes
EMBED_MARKDOWN_CLASS = "embed-markdown"
EMBED_IMAGE_CLASS = "embed-image"
EMBED_IMAGE_DATA_WIDTH = "data-width"
INTERNAL_LINK_CLASS = "link-internal"
EXTERNAL_LINK_CLASS = "link-external"
WIKILINK_LINK_CLASS = "link-wikilink"

##############
# CONVERSION #
##############

def _convert_md_to_html(
        text_md :str,
        verbose :bool = False,
):
    text_md = _replace_embeds(text_md, verbose=verbose)
    text_md = _replace_wikilinks(text_md, verbose=verbose)
    text_md = _smart_insert_spacing(text_md)
    text_html = md.markdown(text_md, extensions=["toc"])
    text_html = _mark_link_types(text_html, verbose=verbose)
    if verbose:
        print(f"------TO HTML------\n{text_html[:min(len(text_html), PREVIEW_LENGTH)]}{"..." if len(text_html) > PREVIEW_LENGTH else ""}\n-----END OF HTML-----")
    return text_html

###############
## Wikilinks ##
###############

def _replace_wikilinks(
        text_md :str,
        verbose :bool = False
) -> str:
    def i_replace(match):
        inner = match.group(1)
        target, display = _parse_obsidian_link(inner)
        base, anchor = _split_anchor(target)
        href = _convert_md_href_to_html(base, anchor)
        html = f'<a href="{href}" class="{WIKILINK_LINK_CLASS}">{display}</a>'
        if verbose:
            print(f'Converted wikilink "[[{inner}]]" to "{html}"')
        return html
    # regex to find all wikilinks [[<anything>]]
    return re.sub(r"\[\[([^\[\]]+)\]\]", i_replace, text_md)

def _parse_obsidian_link(inner :str):
    """
    Parses [[target|display]] or ![[target|display]]
    """
    if "|" in inner:
        target, display = inner.split("|", 1)
    else:
        target, display = inner, inner
    return target.strip(), display.strip()

def _split_anchor(target :str):
    if "#" in target:
        base, anchor = target.split("#", 1)
        return base.strip(), anchor.strip()
    else:
        return target.strip(), None

def _slugify_heading(text :str):
    """Matches Python-Markdown TOC/Obsidian style: lowercase, dashes for spaces, strip most punctuation."""
    text = text.strip().lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'\s+', '-', text)
    text = text.strip('-')
    return text

def _convert_md_href_to_html(
        base    :str,
        anchor  :str =None
) -> str:
    if base.lower().endswith('.md'):
        base = base[:-3]
    base_encoded = quote(base, safe="/")
    href = f"{base_encoded}.html"
    if anchor:
        slug = _slugify_heading(anchor)
        href += f"#{slug}"
    return href

### Block refs ###

def _has_block_ref(
        heading :str,
) -> bool:
    return "^" in heading

# NOTE: I may not implement this since I never use block references personally.
def _replace_block_reference(
        heading :str,
        verbose :bool = False
) -> str:
    raise ValueError("Not implemented")
    return heading

#######################
## Smart Adjustments ##
#######################

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

####################
## Callouts/Notes ##
####################

def _replace_callouts(
        text_md :str,
        verbose :bool = False
) -> str:
    """See [Callouts](https://help.obsidian.md/callouts) for documentation."""
    return ""

############
## Embeds ##
############

def _replace_embeds(
        text_md :str,
        verbose :bool = False
) -> str:
    text_md = _replace_embedded_images(text_md, verbose=verbose)
    _catch_embedded_misc(text_md, verbose=verbose)
    text_md = _replace_embedded_md(text_md, verbose=verbose)    # NOTE: Always run last, as it will treat any input file type as markdown
    return text_md

### Embed Markdown ###

# NOTE: Does not embed markdown. Links to corresponding markdown HTML file.
def _replace_embedded_md(
        text_md :str,
        verbose :bool = False
) -> str:
    def i_replace(match):
        inner = match.group(1)
        target, display = _parse_obsidian_link(inner)
        base, anchor = _split_anchor(target)
        href = _convert_md_href_to_html(base, anchor)
        html = f'<div class="{EMBED_MARKDOWN_CLASS}"><a href="{href}">{display}</a></div>'
        if verbose:
            print(f'Converted embed markdown "![[{inner}]]" to "{html}"')
        return html
    md_pattern = r'!\[\[([^\[\]|]+(?:(?:\.md))?(?:#[^\[\]|]+)?(?:\|[^\[\]]*)?)\]\]'
    return re.sub(md_pattern, i_replace, text_md, flags=re.IGNORECASE)

### Embed Images ###

def _replace_embedded_images(
        text_md :str,
        verbose :bool = False
) -> str:
    def i_replace(match):
        inner = match.group(1)
        if "|" in inner:
            src, *opts = [s.strip() for s in inner.split("|")]
            options = "|".join(opts)
            alt, width = _parse_obsidian_image_options(options)
        else:
            src = inner.strip()
            alt = src
            width = None
        html = f'<img src="{src}" class="{EMBED_IMAGE_CLASS}" alt="{alt}"'
        if width:
            html += f' {EMBED_IMAGE_DATA_WIDTH}="{width}"'
        html += ">"
        if verbose:
            print(f'Converted embed image "![[{inner}]]" to "{html}"')
        return html
    image_pattern = r'!\[\[([^\[\]|]+\.(?:png|jpe?g|gif|svg|webp)(?:\|[^\[\]]*)*)\]\]'
    return re.sub(image_pattern, i_replace, text_md, flags=re.IGNORECASE)

def _parse_obsidian_image_options(options: str):
    """
    Parses Obsidian-style options like 'Alt text|400' or just '400'.
    """
    parts = [p.strip() for p in options.split("|")]
    if len(parts) == 1:
        if parts[0].isdigit():
            return ("", parts[0])
        else:
            return (parts[0], None)
    elif len(parts) == 2:
        if parts[1].isdigit():
            return (parts[0], parts[1])
        else:
            return (parts[0], None)
    else:
        return (options, None)

### Embed Misc ###

def _catch_embedded_misc(
        text_md :str,
        verbose :bool = False
) -> str:
    misc_pattern = r'!\[\[([^\[\]|]+\.(?!md$)[^\[\]|]+)\]\]'
    def i_replace(match):
        inner = match.group(1)
        message = f'Unhandled Obsidian embed: \"![[{inner}]]\"'
        if verbose:
            print(f'ERROR: {message}')
        raise ValueError(message)
    return re.sub(misc_pattern, i_replace, text_md, flags=re.IGNORECASE)

###########
## Tasks ##
###########

def _replace_tasks(
        text_md :str,
        verbose :bool = False
) -> str:
    return ""

##########
## Tags ##
##########

def _replace_tags(
        text_md :str,
        verbose :bool = False
) -> str:
    return ""

##########
## Code ##
##########

def _replace_code_inline(
        text_md :str,
        verbose :bool = False
) -> str:
    """Example: `int x = 10`"""
    return ""

def _replace_code_blocks(
        text_md :str,
        verbose :bool = False
) -> str:
    """Example:
    ~~~python
    var x = 10
    ~~~
    """
    return ""

##########
## YAML ##
##########

# NOTE: I may not implement this since I never use YAML metadata personally.
def _replace_YAML(
        text_md :str,
        verbose :bool = False
) -> str:
    return ""

############
## Tables ##
############

# NOTE: This may already be handled by the markdown plugin
def _replace_tables(
        text_md :str,
        verbose :bool = False
) -> str:
    return ""

###############
## Footnotes ##
###############

def _replace_footnotes(
        text_md :str,
        verbose :bool = False
) -> str:
    return ""

##########
## Math ##
##########

# NOTE: I may not implement this since I never use math inline/blocks.
def _replace_math(
        text_md :str,
        verbose :bool = False
) -> str:
    return ""

###############
## Highlight ##
###############

def _replace_highlight(
        text_md :str,
        verbose :bool = False
) -> str:
    return ""

###################
## Strikethrough ##
###################

# NOTE: This may already be handled by the markdown plugin
def _replace_strikethrough(
        text_md :str,
        verbose :bool = False
) -> str:
    return ""

##############
## Comments ##
##############

# NOTE: I may not implement this since I never use comments.
def _replace_comments(
        text_md :str,
        verbose :bool = False
) -> str:
    return ""

############################
## Signify External Links ##
############################

def _mark_link_types(
        text_html   :str,
        verbose     :bool = True
) -> str:
    soup = BS(text_html, "html.parser")
    for a in soup.find_all('a'):
        href = a.get('href', '')
        if href.startswith(('http://', 'https://', 'mailto:')):
            a['class'] = (a.get('class', []) or []) + [f'{EXTERNAL_LINK_CLASS}']
        elif href.endswith('.html'):
            a['class'] = (a.get('class', []) or []) + [f'{INTERNAL_LINK_CLASS}']
    return str(soup)

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
    base, type = path.splitext(path_md)
    if type != "" and type != ".md":
        return path_md
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