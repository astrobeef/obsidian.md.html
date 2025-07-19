# Goal
## What this is
A CLI which sweeps through directories to convert markdown files to HTML, accounting for (ideally) all of Obsidian's unique markdown handlings.
This lays the foundation for-- but does not provide-- advanced Obsidian features like the [interactive graph](https://help.obsidian.md/plugins/graph), [backlinks](https://help.obsidian.md/plugins/backlinks), and [outgoing links](https://help.obsidian.md/plugins/outgoing-links).

## What this is not
This does not automatically style the converted HTML to look like Obsidian. This program is meant to be a minimal framework for converting to HTML. With that said, all of Obsidian's unique stylings will have corresponding classes/ids/types so that clarity is not lost. For example, [Callouts](https://help.obsidian.md/callouts) will be wrapped in `<div>` blocks with the `callout` class. The `callout` class does not have any built-in stylings.
Nor does this provide advanced Obsidian features.
Nor does this restructure the file hierarchy to reflect a standard site structure. Files will exist alongside their markdown origins for simplicity.

# Progress
- See [[test]] for proof of conversions
- [x] - Basic conversion working (no style; no header; no Obsidian specific conversions)
- [x] - Obsidian markdown handling
    - [x] - wikilinks
    - [x] - smart styling (spaces before certain items like lists, headings, tags)
    - [x] - Anchors
    - [ ] - Block references
    - [x] - Callouts (encapsulate callout notes with unique classes based on callout type)
    - [x] - Embedded notes/files
    - [x] - Wiki-style headers/section linking
    - [x] - Tasks
    - [x] - Tags
    - [x] - Code inline
    - [x] - Code blocks
    - [ ] - YAML
    - [x] - Footnotes
    - [x] - Math
    - [x] - Highlighting
    - [x] - Strikethrough
    - [x] - Comments
- [x] - CLI Tool
    - [x] - Convert individual files or entire directory
    - [x] - Ignore list to ignore certain subdirectories (like .gitignore)
    - [ ] - ~~Keep a list of generated files for easy deletion~~
    - [x] - Setup to run as a global tool for any project
- [x] - Template for CSS/JS
- [ ] - ISSUE: Obsidian will automatically shortern internal link paths to be the shortest unique path ("_media/image.png" -> "image.png" if not conflicting files)
- [ ] - I use the extension ".md.html" for clarity, but most HTML projects expect an entry file "index.html". I should have-- or at least as an option-- a unique case for renaming the "index.md" file to "index.html".


# Setting Up Environment
(Mainly for me) To set up python environment on Windows, run these commands:
1. `py -m venv .venv`
2. `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process`
3. `.\.venv\Scripts\activate`

# Dependencies
- [markdown](https://pypi.org/project/Markdown/)
- [pymdown-extensions](https://pypi.org/project/pymdown-extensions/)

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

## Math (Optional MathJax CDN)
Math inline/blocks are in a unique position amongst all of the conversions because math cannot be rendered natively in HTML. Some sort of renderer is required, such as [MathJax](https://docs.mathjax.org/en/latest/web/start.html). While this project is not meant to implement any sort of styling, it feels incomplete to leave out math rendering. But since it goes against the premise of the project to include any JS, I have set up an option to embed the MathJax CDN into files which display math (even if the option is enabled, it will not be embeded into pages which don't use math inline/blocks).
- As of now, MathJax can be enabled during conversion with the CLI option `--mathjax`. Otherwise it is excluded and it is up to the user to set up math rendering.
- Regardless, math inline/blocks are encapsulated with distinct classes so a user can handle them as they see fit. 