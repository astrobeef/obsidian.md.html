# Progress
Goal is to have a CLI which can sweep a repo for all *.md files and convert them to .html, leveraging a template for styling.
- [x] - Basic conversion working (no style; no header; no Obsidian specific conversions)
- [ ] - Obsidian markdown handling
    - [x] - wikilinks
    - [x] - smart styling (spaces before certain items like lists, headings, tags)
    - [ ] - Callouts (display notes with unique borders/styling)
    - [ ] - Embedded notes/files
    - [ ] - Wiki-style headers/section linking

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