import fnmatch
import os

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