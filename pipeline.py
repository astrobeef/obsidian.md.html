# Third-party
import markdown as md
# First-party
from collections import defaultdict
# Local
from constants import PREVIEW_LENGTH
from convert import replace_comments, smart_insert_spacing, smart_single_newlines, replace_math, replace_highlight, replace_strikethrough, replace_code, replace_callouts, replace_embeds, replace_wikilinks, replace_tags, mark_link_types, is_mathjax_necessary, embed_MathJax_scripting

def convert_markdown_to_html(
        text_md                 :str,
        file_index              :defaultdict,
        root                    :str,
        tags_use_links          :bool = False,
        embed_mathjax_scripting :bool = False,
        verbose                 :bool = False,
):
    text_md = replace_comments(text_md, verbose=verbose)
    text_md = smart_insert_spacing(text_md)
    text_md = smart_single_newlines(text_md, verbose=verbose)
    text_md = replace_math(text_md, verbose=verbose)
    text_md = replace_highlight(text_md, verbose=verbose)
    text_md = replace_strikethrough(text_md, verbose=verbose)
    text_md = replace_code(text_md, verbose=verbose)
    text_md = replace_callouts(text_md, verbose=verbose)
    text_md = replace_embeds(text_md, file_index, root, verbose=verbose)
    text_md = replace_wikilinks(text_md, file_index, root, verbose=verbose)
    text_md = replace_tags(text_md, use_links=tags_use_links, verbose=verbose)
    text_html = md.markdown(text_md, extensions=["toc", "pymdownx.tasklist", "tables", "footnotes"])
    text_html = mark_link_types(text_html, verbose=verbose)
    if embed_mathjax_scripting and is_mathjax_necessary(text_md):
        text_html += embed_MathJax_scripting()
    if verbose:
        print(f"------TO HTML------\n{text_html[:min(len(text_html), PREVIEW_LENGTH)]}{"..." if len(text_html) > PREVIEW_LENGTH else ""}\n-----END OF HTML-----")
    return text_html