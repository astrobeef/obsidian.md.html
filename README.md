# obsidian-md-html

Convert any [Obsidian](https://obsidian.md/) vault (or a single note) to plain, template-ready **HTML** from the command line. Handles Obsidian's unique markdown handlings (such as [wikilinks](https://help.obsidian.md/links)) and provides clear types/classes/data for Obsidian specific properties (such as [tags](https://help.obsidian.md/tags)). This does not implement Obsidian features (such as the [interactive graph](https://help.obsidian.md/plugins/graph)), but it does lay the foundation for your own implementation.

The tool writes side-by-side HTML files:
- note.md        →  note.md.html
- index.md       →  index.html   (special case)

---

## What It Covers
Obsidian wikilinks, headings, callouts, tags, tasks, embeds (image/audio/video/PDF/md), math, footnotes, highlight, strikethrough, comments, smart single-newline & list/heading spacing.

Each feature gets a sensible HTML structure. CSS-hook classes are generated, but stylings are not.

This tool is not published to PyPI because it is just a hobby project, but it's robust enough for me to use regularly.

## Example
I use this tool to build my Github Page: [astrobeef.github.io](https://astrobeef.github.io/Projects/Obsidian%20Markdown%20to%20HTML%20Converter.md.html)

## Dependencies
- [markdown](https://pypi.org/project/Markdown/)
- [pymdown-extensions](https://pypi.org/project/pymdown-extensions/)

## Install & Update

```bash
# clone fork or this repo
git clone https://github.com/astrobeef/obsidian.md_to_html.git
cd obsidian.md_to_html

# install in the active Python (≥3.8) environment
pip install .

# update after pulling new commits
pip install --upgrade .
# remove
pip uninstall obsidian-md-html
```

### Updating After Local Changes

When making local changes to this git project, any new changes can be updated to the package by running:

`git install --upgrade .`

## Quick Use
```bash
# convert every .md file under the current directory
obsidian-md-html

# convert a specific folder
obsidian-md-html notes/

# convert one file
obsidian-md-html README.md

# clean built files (including "index.html")
obsidian-md-html --clean --index
```

## Flags
| flag                   | purpose                                                                                          |
| ---------------------- | ------------------------------------------------------------------------------------------------ |
| `--taglinks`           | turn #tags into clickable `<a>` links (default buttons)                                          |
| `--mathjax`            | embed MathJax CDN script when a page contains `$…$` or `$$…$$`                                   |
| `--template path.html` | wrap output in a custom HTML template (`{title}` & `{content}` placeholders)                     |
| `--verbose`            | print debug messages                                                                             |
| `--clean [-f] [-i]`    | delete all generated `*.md.html` files (`-i` also removes `index.html`, `-f` skips confirmation) |

## Global CSS (Optional)

If you include `{global_css}` in your template and a `global.css` file in your root directory, then it will be automatically embed into all HTML files. The name of the css file can be changes in constants.py.

## Ignoring Files

Add to the .convertignore (same syntax as .gitignore) skip files or folders during conversion.

## Setting Up Environment

(Mainly for me) To set up python environment on Windows, run these commands:
1. `py -m venv .venv`
2. `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process`
3. `.\.venv\Scripts\activate`

## Tags

To handle tags, I have the option to use `<a>` element types, which would make the tags clickable. This would be useful for a site without JavaScript to enable a pseudo-search feature which links to a dedicated page for the tag. The dedicated page would include links for every occurance of the tag. However, if I don't consider this restriction, it would be more modern for the elements to be `<span>`. JavaScript could then be used to interact with `<span>` tags in ways that mimic Obsidian interactions.
I'm going to make this an option: use links (for those neglecting JavaScript) or use buttons (for those using JavaScript)

## Math (Optional MathJax CDN)

Math inline/blocks are in a unique position amongst all of the conversions because math cannot be rendered natively in HTML. Some sort of renderer is required, such as [MathJax](https://docs.mathjax.org/en/latest/web/start.html). While this project is not meant to implement any sort of styling, it feels incomplete to leave out math rendering. But since it goes against the premise of the project to include any JS, I have set up an option to embed the MathJax CDN into files which display math (even if the option is enabled, it will not be embeded into pages which don't use math inline/blocks).
- As of now, MathJax can be enabled during conversion with the CLI option `--mathjax`. Otherwise it is excluded and it is up to the user to set up math rendering.
- Regardless, math inline/blocks are encapsulated with distinct classes so a user can handle them as they see fit.

## Non-existent Markdown Links
In Obsidian, it's possible for a wikilink to have no corresponding markdown file. In this case, the link is given the "#" href path by default, but this can be set to any path in the constants.py file. The link is also given a unique class to differentiate it from regular wikilinks, making it easy to style individually.