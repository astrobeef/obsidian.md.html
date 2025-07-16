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
    - [ ] - Anchors
    - [ ] - Block references
    - [ ] - Callouts (encapsulate callout notes with unique classes based on callout type)
    - [ ] - Embedded notes/files
    - [ ] - Wiki-style headers/section linking
    - [ ] - Tasks
    - [ ] - Tags
    - [ ] - Code inline
    - [ ] - Code blocks
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

# Log

## Wikilinks
Parsing wikilinks is pretty simple. A regex operation is used to find all occurrences, then those are replaced with HTML links. The current implementation assumes the path to the HTML is the same as the path to the MD.