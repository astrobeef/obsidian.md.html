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

# Callout Test

> [!note] This note is a callout
> This is a note


# Embedded Notes/Files Test
![[README]]
![[_images/bruno.webp|300]]

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
![[_media/example.ogg]]
![[_media/example.mp4]]
![[_media/example.pdf]]