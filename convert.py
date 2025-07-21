# First-party
from collections import defaultdict
from os import path
from urllib.parse import quote
import re
import html
# Local
from constants import *
from util import resolve_obsidian_path

##############
# CONVERSION #
##############

###############
## Wikilinks ##
###############

def replace_wikilinks(
        text_md     :str,
        file_index  :defaultdict,
        root        :str,
        verbose     :bool = False
) -> str:
    def i_replace(match):
        inner = match.group(1)
        target, display = _parse_obsidian_link(inner)
        href = _convert_md_href_to_html(target, file_index, root)
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

def _split_anchor_and_block(target: str
) -> tuple[str, str | None, str | None]:
    """
    Returns (base, anchor, block_id), splitting on # and ^ if present.
    """
    anchor, block = None, None
    # Split block first (since ^ can appear after #)
    if "^" in target:
        target, block = target.split("^", 1)
        block = block.strip()
    if "#" in target:
        target, anchor = target.split("#", 1)
        anchor = anchor.strip()
    return target.strip(), anchor, block

def _slugify_heading(text :str):
    """Matches Python-Markdown TOC/Obsidian style: lowercase, dashes for spaces, strip most punctuation."""
    text = text.strip().lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'\s+', '-', text)
    text = text.strip('-')
    return text

def _convert_md_href_to_html(
        target: str,
        file_index: defaultdict,
        current_dir: str,
) -> str:
    """
    Build the final href for a markdown file,
    using the relative path returned by `resolve_obsidian_path`.
    """
    base, anchor, block = _split_anchor_and_block(target)
    rel_path = resolve_obsidian_path(base, file_index, current_dir)
    if rel_path.lower().endswith(".md"):
        rel_path = rel_path[:-3]
    # Unique case for "index.html" to ensure it matches naming convention
    if path.basename(rel_path) == "index":
        href = f"{rel_path}.html"
    else:
        href = f"{rel_path}{BUILT_HTML_EXTENSION}"
    fragment = ""
    if block:  # block IDs should go before anchors due to Obsidian
        fragment = f"^{block}"
    elif anchor:
        fragment = f"#{_slugify_heading(anchor)}"
    if fragment:
        href += fragment
    return quote(href, safe="/")

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

def smart_insert_spacing(
        text_md :str
) -> str:
    """Obsidian is smarter with markdown styling than traditional markdown displayers. For example, a list in markdown traditionally requires a space prior to note that it's a list. But Obsidian is smart enough to know it's a list and will display it as such."""
    list_pattern = re.compile(
        r"([^\n])\n(\s*(?:\d+\.\s+|\-\s+|\*\s+|\-\s*\[.\]\s+|\*\s*\[.\]\s+))"
    )
    text_md = list_pattern.sub(r"\1\n\n\2", text_md)
    heading_pattern = re.compile(r"([^\n])\n(\s*#{1,6}\s+)")
    text_md = heading_pattern.sub(r"\1\n\n\2", text_md)
    code_fence_pattern = re.compile(r'([^\n])\n([ \t]*(?:```|~~~))')
    text_md = code_fence_pattern.sub(r"\1\n\n\2", text_md)
    return text_md

def smart_single_newlines(
        text_md :str,
        verbose :bool
) -> str:
    """Obsidian is smarter with markdown styling than traditional markdown displayers. In typical markdown viewers, a series of text on newlines will not be respected. Instead, text will be snapped onto one line. In Obsidian, single newlines are respected. This is such a core part of Obsidian notes that it should be built into the converter."""
    pattern = re.compile(r'([^\n])\n(?!\n)(?![ \t]*(?:```|~~~))')
    result = pattern.sub(r'\1  \n', text_md)
    if verbose:
        print("After single-newline preservation (code-fence lines skipped):\n", result)
    return result

####################
## Callouts/Notes ##
####################

def replace_callouts(text_md: str, verbose: bool = False) -> str:
    """
    Converts Obsidian callouts into a single <p class="{CALLOUT_CONTENT_CLASS}">...</p>
    with <br> between content lines, matching blockquote behavior (default markdown conversion for blockquotes).
    """
    callout_pat = re.compile(
        r'(^> \[!(\w+)\](?:[ \t]+(.+))?\n'      # first line: type + optional title
        r'((?:^>.*\n?)*)'                       # following quote lines (may be empty)
        r')', re.MULTILINE)
    def repl(m):
        ctype = m.group(2).lower()
        title = (m.group(3) or '').strip()
        raw   = m.group(4)
        # Gather all lines (may be empty)
        lines = raw.splitlines()
        content_lines = []
        for ln in lines:
            if ln.startswith('>'):
                ln = ln[1:]
                if ln.startswith(' '):
                    ln = ln[1:]
            # Include all lines
            content_lines.append(html.escape(ln))
        # Remove any leading blank content line (from single-line callout)
        while content_lines and not content_lines[0].strip():
            content_lines = content_lines[1:]
        # Remove any trailing blank lines (not needed for rendering)
        while content_lines and not content_lines[-1].strip():
            content_lines = content_lines[:-1]
        # Join content with <br>
        body_html = ('<p class="{CALLOUT_CONTENT_CLASS}">'
                     + '<br>\n'.join(content_lines) +
                     '</p>') if content_lines else '<p class="{CALLOUT_CONTENT_CLASS}"></p>'
        title_html = (f'<p class="{CALLOUT_TITLE_CLASS}">{html.escape(title)}</p>'
                      if title else '')
        html_block = (
            f'<blockquote class="{CALLOUT_CLASS} {CALLOUT_TYPE_CLASS_PREFIX}{ctype}" '
            f'{CALLOUT_TYPE_DATA}="{ctype}">\n'
            f'{title_html}\n{body_html}\n'
            f'</blockquote>'
        )
        if verbose:
            print(f'Converted {ctype} call-out, title="{title}", '
                  f'lines={len(content_lines)}')
        return html_block
    return callout_pat.sub(repl, text_md)

############
## Embeds ##
############

def replace_embeds(
        text_md     :str,
        file_index  :defaultdict,
        root        :str,
        verbose     :bool = False
) -> str:
    text_md = _replace_embedded_images(text_md, file_index, root, verbose=verbose)
    text_md = _replace_embedded_audio(text_md, file_index, root, verbose=verbose)
    text_md = _replace_embedded_video(text_md, file_index, root, verbose=verbose)
    text_md = _replace_embedded_pdf(text_md, file_index, root, verbose=verbose)
    _catch_embedded_misc(text_md, verbose=verbose)
    text_md = _replace_embedded_md(text_md, file_index, root, verbose=verbose)    # NOTE: Always run last, as it will treat any input file type as markdown
    return text_md

### Embed Markdown ###

# NOTE: Does not embed markdown. Links to corresponding markdown HTML file.
def _replace_embedded_md(
        text_md     :str,
        file_index  :defaultdict,
        root        :str,
        verbose     :bool = False
) -> str:
    def i_replace(match):
        inner = match.group(1)
        target, display = _parse_obsidian_link(inner)
        href = _convert_md_href_to_html(target, file_index, root)
        html = f'<div class="{EMBED_MARKDOWN_CLASS}"><a href="{href}">{display}</a></div>'
        if verbose:
            print(f'Converted embed markdown "![[{inner}]]" to "{html}"')
        return html
    md_pattern = r'!\[\[([^\[\]|]+(?:(?:\.md))?(?:#[^\[\]|]+)?(?:\|[^\[\]]*)?)\]\]'
    return re.sub(md_pattern, i_replace, text_md, flags=re.IGNORECASE)

### Embed Images ###

def _replace_embedded_images(
        text_md     :str,
        file_index  :defaultdict,
        root        :str,
        verbose     :bool = False
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
        src = resolve_obsidian_path(src, file_index, root)
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

### Embed Audio ###

def _replace_embedded_audio(
        text_md     :str,
        file_index  :defaultdict,
        root        :str,
        verbose     :bool = False
) -> str:
    def i_replace(match):
        inner = match.group(1)
        src = inner.strip()
        src = resolve_obsidian_path(src, file_index, root)
        html = f'<audio controls class="{EMBED_AUDIO_CLASS}"><source src="{src}"></audio>'
        if verbose:
            print(f'Converted embed audio "![[{inner}]]" to "{html}"')
        return html
    audio_pattern = r'!\[\[([^\[\]|]+\.(?:mp3|wav|ogg|flac|m4a|aac|opus))\]\]'
    return re.sub(audio_pattern, i_replace, text_md, flags=re.IGNORECASE)

### Embed Video ###

def _replace_embedded_video(
        text_md     :str,
        file_index  :defaultdict,
        root        :str,
        verbose     :bool = False
) -> str:
    def i_replace(match):
        inner = match.group(1)
        src = inner.strip()
        src = resolve_obsidian_path(src, file_index, root)
        html = f'<video controls class="{EMBED_VIDEO_CLASS}"><source src="{src}"></video>'
        if verbose:
            print(f'Converted embed video "![[{inner}]]" to "{html}"')
        return html
    video_pattern = r'!\[\[([^\[\]|]+\.(?:mp4|webm|ogv|mov|mkv))\]\]'
    return re.sub(video_pattern, i_replace, text_md, flags=re.IGNORECASE)

### Embed PDF ###

def _replace_embedded_pdf(
        text_md     :str,
        file_index  :defaultdict,
        root        :str,
        verbose     :bool = False
) -> str:
    def i_replace(match):
        inner = match.group(1)
        src = inner.strip()
        src = resolve_obsidian_path(src, file_index, root)
        html = f'<embed src="{src}" type="application/pdf" class="{EMBED_PDF_CLASS}">'
        if verbose:
            print(f'Converted embed PDF "![[{inner}]]" to "{html}"')
        return html
    pdf_pattern = r'!\[\[([^\[\]|]+\.pdf)\]\]'
    return re.sub(pdf_pattern, i_replace, text_md, flags=re.IGNORECASE)

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

##########
## Tags ##
##########

def replace_tags(
        text_md     :str,
        use_links   :bool = False,
        verbose     :bool = False
) -> str:
    if use_links:
        return _replace_tags_with_links(text_md, verbose)
    else:
        return _replace_tags_without_links(text_md, verbose)

def _replace_tags_with_links(text_md: str, verbose: bool = False) -> str:
    """
    Replace #tags with clickable <a> elements.
    """
    def tag_replacer(match):
        tag = match.group(0)
        tag_name = match.group(1)
        tag_href = f"tags/{tag_name}.html"
        html = f'<a class="{TAGS_CLASS}" {TAGS_DATA}="{tag_name}" href="{tag_href}">{tag}</a>'
        if verbose:
            print(f'Converted tag "{tag}" to "{html}"')
        return html
    tag_pattern = re.compile(r'(?<![\w\[\(\{])#([\w/-]+)')
    return tag_pattern.sub(tag_replacer, text_md)

def _replace_tags_without_links(text_md: str, verbose: bool = False) -> str:
    """
    Replace #tags with <button> elements for JS-based/dynamic sites.
    """
    def tag_replacer(match):
        tag = match.group(0)
        tag_name = match.group(1)
        html = f'<button class="{TAGS_CLASS}" {TAGS_DATA}="{tag_name}">{tag}</button>'
        if verbose:
            print(f'Converted tag "{tag}" to "{html}"')
        return html
    tag_pattern = re.compile(r'(?<![\w\[\(\{])#([\w/-]+)')
    return tag_pattern.sub(tag_replacer, text_md)

##########
## Code ##
##########

def replace_code(
        text_md :str,
        verbose :bool = False
) -> str:
    text_md = _replace_code_inline(text_md=text_md, verbose=verbose)
    text_md = _replace_code_blocks(text_md=text_md, verbose=verbose)
    return text_md

def _replace_code_inline(
        text_md :str,
        verbose :bool = False
) -> str:
    """
    Replace inline code surrounded by single backticks (`)
    """
    def replacer(match):
        code = match.group(1)
        code_escaped = html.escape(code)
        html_code = f'<code class="{CODE_INLINE_CLASS}">{code_escaped}</code>'
        if verbose:
            print(f"Converted inline code: `{code}` -> {html_code}")
        return html_code
    pattern = re.compile(r'(?<!`)\`([^\n`]+?)\`(?!`)', re.DOTALL)
    return pattern.sub(replacer, text_md)

def _replace_code_blocks(
        text_md :str,
        verbose :bool = False
) -> str:
    """
    Convert fenced code blocks (```lang or ~~~lang)
    """
    def code_replacer(match):
        fence = match.group(1)
        lang = (match.group(2) or "").strip()
        code = match.group(3)
        code_escaped = html.escape(code)
        class_attr = f' class="{CODE_LANG_CLASS_PREFIX}{lang} {CODE_BLOCK_CLASS}"' if lang else f"class={CODE_BLOCK_CLASS}"
        html_block = f'<pre><code{class_attr}>{code_escaped}</code></pre>'
        if verbose:
            print(f"Converted code block ({lang!r}):\n{code}\n---")
        return html_block
    pattern = re.compile(
        r'(?:^|\n)(```|~~~)[ \t]*([\w+-]*)[ \t]*\n(.*?)(?:\n\1[ \t]*\n?)',
        re.DOTALL
    )
    return pattern.sub(code_replacer, text_md)

##########
## YAML ##
##########

# NOTE: I may not implement this since I never use YAML metadata personally.
def _replace_YAML(
        text_md :str,
        verbose :bool = False
) -> str:
    return ""

##########
## Math ##
##########

def replace_math(
        text_md                 :str,
        verbose                 :bool = False
) -> str:
    """
    Wraps math in HTML containers but leaves $ and $$ delimiters for MathJax/KaTeX.
    """
    # Block math: $$ ... $$
    text_md = re.sub(
        r"\$\$([\s\S]+?)\$\$",
        lambda m: f'<div class="{MATH_BLOCK_CLASS}">$$\n{m.group(1).strip()}\n$$</div>',
        text_md
    )
    # Inline math: $...$
    text_md = re.sub(
        r"\$([^\$\n]+?)\$",
        lambda m: f'<span class="{MATH_INLINE_CLASS}">${m.group(1).strip()}$</span>',
        text_md
    )
    if verbose:
        print("Math blocks and inline math replaced with wrappers (delimiters kept).")
    return text_md

def embed_MathJax_scripting() -> str:
    """Returns the MathJax script block for HTML output."""
    return """
<script>
window.MathJax = {
tex: {
    inlineMath: [['$', '$']],
    displayMath: [['$$', '$$']]
},
options: {
    skipHtmlTags: ["script", "noscript", "style", "textarea", "pre", "code"]
}
};
</script>
<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
"""

def is_mathjax_necessary(text_md: str) -> bool:
    """Returns True if math blocks or inline math are present."""
    return bool(re.search(r'\$\$[\s\S]+?\$\$|\$[^\$\n]+?\$', text_md))

###############
## Highlight ##
###############

def replace_highlight(text_md: str, verbose: bool = False) -> str:
    text_md = re.sub(r'==(.+?)==', r'<mark>\1</mark>', text_md)
    if verbose:
        print("Highlight replaced.")
    return text_md

###################
## Strikethrough ##
###################

def replace_strikethrough(
        text_md :str,
        verbose :bool = False
) -> str:
    """
    Converts ~~strikethrough~~ to <del>strikethrough</del>.
    """
    # Replace any non-greedy sequence between double tildes with <del>
    result = re.sub(r'~~(.*?)~~', r'<del>\1</del>', text_md)
    if verbose:
        print("Strikethrough replaced.")
    return result

##############
## Comments ##
##############

def replace_comments(text_md: str, verbose: bool = False) -> str:
    # Remove block comments: %% ... %%
    text_md = re.sub(r'%%[\s\S]*?%%', '', text_md)
    if verbose:
        print("Obsidian comments removed.")
    return text_md

############################
## Signify External Links ##
############################

import re
from constants import EXTERNAL_LINK_CLASS, INTERNAL_LINK_CLASS

def mark_link_types(text_html: str, verbose: bool = False) -> str:
    """
    Add EXTERNAL_LINK_CLASS or INTERNAL_LINK_CLASS to <a> tags
    """
    # Regex to capture full <a ...> tag, the attribute list, and the href value.
    a_tag_re = re.compile(
        r'<a\b([^>]*?\bhref\s*=\s*["\'])([^"\']+)(["\'][^>]*)>',
        flags=re.IGNORECASE | re.DOTALL,
    )
    def _add_class(tag_attrs: str, href: str, tail: str, tag_full: str) -> str:
        add_cls = None
        if href.startswith(("http://", "https://", "mailto:")):
            add_cls = EXTERNAL_LINK_CLASS
        elif href.lower().endswith(".html"):
            add_cls = INTERNAL_LINK_CLASS
        if not add_cls:
            return tag_full
        # Does the tag already have a class attribute?
        class_match = re.search(r'\bclass\s*=\s*["\']([^"\']*)', tag_attrs, flags=re.IGNORECASE)
        if class_match:
            classes = class_match.group(1).split()
            if add_cls not in classes:
                classes.append(add_cls)
                new_class_attr = f'class="{ " ".join(classes) }"'
                tag_attrs = (
                    tag_attrs[: class_match.start()]
                    + new_class_attr
                    + tag_attrs[class_match.end() :]
                )
        else:
            tag_attrs = ' class="{}"{}'.format(add_cls, tag_attrs)
        if verbose:
            print(f'[{add_cls}] ← {href}')
        return f"<a{tag_attrs}{href}{tail}>"
    result_parts = []
    pos = 0
    for m in a_tag_re.finditer(text_html):
        start, end = m.span()
        attrs_prefix, href_val, attrs_suffix = m.groups()
        result_parts.append(text_html[pos:start])
        new_tag = _add_class(attrs_prefix, href_val, attrs_suffix, m.group(0))
        result_parts.append(new_tag)
        pos = end
    result_parts.append(text_html[pos:])
    return "".join(result_parts)
