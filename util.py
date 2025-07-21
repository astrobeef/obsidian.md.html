# First-party
import fnmatch
import os
from collections import defaultdict

def parse_ignore_file(ignore_path):
    patterns = []
    try:
        with open(ignore_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    patterns.append(line)
    except FileNotFoundError:
        pass
    return patterns

def should_ignore_files(rel_path, patterns, is_dir=False):
    # Normalize path (always use forward slashes for matching)
    rel_path_norm = rel_path.replace("\\", "/").rstrip("/")
    for pat in patterns:
        pat = pat.strip()
        if not pat:
            continue
        if pat.endswith("/"):
            pat_dir = pat.rstrip("/")
            if is_dir and fnmatch.fnmatch(rel_path_norm, pat_dir):
                return True
            if rel_path_norm.startswith(pat_dir + "/"):
                return True
        else:
            if fnmatch.fnmatch(rel_path_norm, pat):
                return True
            if is_dir and fnmatch.fnmatch(rel_path_norm + "/", pat + "/"):
                return True
    return False

def build_file_index(base_dir: str) -> defaultdict:
    """
    Scans base_dir and returns {lowercase filename: [relative_path, ...]}
    """
    file_map = defaultdict(list)
    base_dir_abs = os.path.abspath(base_dir)
    for root, _dirs, files in os.walk(base_dir_abs):
        for name in files:
            file_map[name.lower()].append(os.path.join(root, name))
    return file_map

def _try_resolve_markdown_path(
        link_text   :str,
        file_map    :defaultdict,
        candidates
):
    if not candidates:
        # If no extension (as is common in Obsidian for markdown), try adding ".md"
        if '.' not in link_text:
            alt_md = link_text + '.md'
            candidates = file_map.get(alt_md.lower())
            return _try_resolve_markdown_path(link_text, file_map, candidates)
        else:
            raise FileNotFoundError(f"No candidate for Obsidian link: {link_text}")           # nothing found
    return candidates

def resolve_obsidian_path(
        link_text   :str,
        file_map    :defaultdict,
        current_dir :str
) -> str:
    """
    Given 'image.png', 'some/dir', and the file_map, return best relative path for the link (to match Obsidian's similar path resolution system).
    """
    current_dir = os.path.abspath(current_dir)
    candidates = file_map.get(link_text.lower())
    if not candidates:
        candidates = _try_resolve_markdown_path(link_text, file_map, candidates)
    if len(candidates) == 1:
        # single match -> easy
        return os.path.relpath(candidates[0], current_dir).replace("\\", "/")
    else:
        # several matches -> prefer the one that shares the longest prefix (Obsidian heuristics)
        best = None
        best_len = -1
        for cand in candidates:
            common = os.path.commonpath([current_dir, cand])
            length = len(common)
            if length > best_len:
                best = cand
                best_len = length
        return os.path.relpath(best, current_dir).replace("\\", "/")