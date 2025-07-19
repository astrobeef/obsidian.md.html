# Wikilinks Test
This is an example markdown file linking to [[README]] using Obsidian wikilinks.

# Spacing Test
## Headings ++ Test H2
## List test
1. Hello
2. World
### Bullet
- Hello
- World
### Checklist (unchecked)
- [ ] Hello
- [ ] World
### Checklist (checked)
- [x] Hello
- [x] World

# Note / Callout Test

> note without callout
> this is a note without a callout

> [!note] This note is a callout
> This is a note
> This is another line of the note
> This is a third line of the note

> [!tip] This tip is a callout
> This is a tip
> This is another line of the tip
> This is a third line of the tip

# Embedded Notes/Files Test
![[README]]
![[bruno.webp|300]]

# Wiki Headers/Section Links
[[README#Setting Up Environment]]

# Tag Tests
Should be considered tags:
#test
This is a note with a #tag inside.
#one #two #three
#tag_123 #tag_test2.
#my-tag #another-tag
#parent/child
Should not be considered tags:
(#tag1) , [#tag2] , {#tag}

# Table Test

| Header 1 | Header 2 | Header 3 |
|----------|----------|----------|
| Row 1A   | Row 1B   | Row 1C   |
| Row 2A   | Row 2B   | Row 2C   |

# Footnote Test

Here is a statement with a footnote.[^1]

[^1]: This is the footnote content.

# Math Test

Inline math: $x^2 + y^2 = z^2$

Block math:
$$
\int_{-\infty}^{\infty} e^{-x^2} dx = \sqrt{\pi}
$$

# Highlight Test

==This text should be highlighted in Obsidian.==

# Strikethrough Test

~~This text should be highlighted in Obsidian.~~

# Comment Test

%% This is a block comment in Obsidian and should not appear in output %%
Here is normal text.

# Code Inline
Some code: `int x = 10`

# Code Block Test
## Heading 2
~~~python
    ## Comment that might be parsed like a heading
    def _convert_md_to_html(
            text_md         :str,
            tags_use_links  :bool = False,
            verbose         :bool = False,
    ):
        text_md = _replace_embeds(text_md, verbose=verbose)
        text_md = _replace_wikilinks(text_md, verbose=verbose)
        text_md = _replace_tags(text_md, use_links=tags_use_links, verbose=verbose)

        text_md = _smart_single_newlines(text_md, verbose=verbose)
        text_md = _smart_insert_spacing(text_md)
        text_html = md.markdown(text_md, extensions=["toc", "pymdownx.tasklist"])
        text_html = _mark_link_types(text_html, verbose=verbose)
        if verbose:
            print(f"------TO HTML------\n{text_html[:min(len(text_html), PREVIEW_LENGTH)]}{"..." if len(text_html) > PREVIEW_LENGTH else ""}\n-----END OF HTML-----")
        return text_html
~~~

# Test Embedding (Continued)
![[example.ogg]]
![[example.mp4]]
![[example.pdf]]
