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

def build_file_index(base_dir) -> defaultdict:
    """
    Scans base_dir and returns {lowercase filename: [relative_path, ...]}
    """
    file_map = defaultdict(list)
    for root, _dirs, files in os.walk(base_dir):
        for name in files:
            rel_path = os.path.relpath(os.path.join(root, name), base_dir)
            file_map[name.lower()].append(rel_path)
    return file_map

def resolve_obsidian_path(
        link_text   :str,
        file_map    :defaultdict,
        root        :str
) -> str:
    """
    Given 'image.png', 'some/dir', and the file_map, return best relative path for the link (to match Obsidian's similar path resolution system).
    """
    candidates = file_map.get(link_text.lower())
    if not candidates:
        return link_text
    if len(candidates) == 1:
        return candidates[0]
    current_dir_parts = os.path.normpath(root).split(os.sep)
    for i in range(len(current_dir_parts), 0, -1):
        prefix = os.path.join(*current_dir_parts[:i])
        for candidate in candidates:
            if candidate.startswith(prefix):
                return candidate
    return candidates[0].replace("\\", "/")