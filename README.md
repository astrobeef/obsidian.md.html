# Goal
## What this is
A CLI which sweeps through directories to convert markdown files to HTML, accounting for (ideally) all of Obsidian's unique markdown handlings.

This lays the foundation for-- but does not provide-- advanced Obsidian features like the [interactive graph](https://help.obsidian.md/plugins/graph), [backlinks](https://help.obsidian.md/plugins/backlinks), and [outgoing links](https://help.obsidian.md/plugins/outgoing-links).

## What this is not
This does not automatically style the converted HTML to look like Obsidian. This program is meant to be a minimal framework for converting to HTML. With that said, all of Obsidian's unique stylings will have corresponding classes/ids/types so that clarity is not lost. For example, [Callouts](https://help.obsidian.md/callouts) will be wrapped in `<div>` blocks with the `callout` class. The `callout` class does not have any built-in stylings.

Nor does this provide advanced Obsidian features.

# Progress
- [x] - Basic conversion working (no style; no header; no Obsidian specific conversions)
- [ ] - Obsidian markdown handling
    - [x] - wikilinks
    - [x] - smart styling (spaces before certain items like lists, headings, tags)
    - [x] - Anchors
    - [ ] - Block references
    - [ ] - Callouts (encapsulate callout notes with unique classes based on callout type)
    - [x] - Embedded notes/files
    - [x] - Wiki-style headers/section linking
    - [x] - Tasks
    - [x] - Tags
    - [x] - Code inline
    - [x] - Code blocks
    - [ ] - YAML
    - [ ] - Footnotes
    - [ ] - Math
    - [ ] - Highlighting
    - [ ] - Strikethrough
    - [ ] - Comments

# Setting Up Environment
To set up python environment, run these commands:
1. `py -m venv .venv`
2. `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process`
3. `.\.venv\Scripts\activate`

# Dependencies
- [markdown](https://pypi.org/project/Markdown/)
- [pymdown-extensions](https://pypi.org/project/pymdown-extensions/)
- [beautifulsoup4](https://pypi.org/project/beautifulsoup4/)

# Log

## Wikilinks
Parsing wikilinks is pretty simple. A regex operation is used to find all occurrences, then those are replaced with HTML links. The current implementation assumes the path to the HTML is the same as the path to the MD.

## Wikilink Anchors
Obsidian allows for linking to headings within a note by using anchor syntax. In order to have this function as expected, all headings need to be given unique IDs. Luckily IDs can be easily inserted with the `markdown` plugin method extension "toc":
~~~python
    text_html = md.markdown(text_md, extensions=["toc"])
~~~
With the IDs made, the next step is to convert the markdown anchors to the TOC id format. For example, convert "Heading Example" to "heading-example", which can be done with regex.

## Tags
To handle tags, I have the option to use `<a>` element types, which would make the tags clickable. This would be useful for a site without JavaScript to enable a pseudo-search feature which links to a dedicated page for the tag. The dedicated page would include links for every occurance of the tag. However, if I don't consider this restriction, it would be more modern for the elements to be `<span>`. JavaScript could then be used to interact with `<span>` tags in ways that mimic Obsidian interactions.
I'm going to make this an option: use links (for those neglecting JavaScript) or use buttons (for those using JavaScript)