import fnmatch


def read_gitignore(gitignore_path):
    with open(gitignore_path, "r") as f:
        lines = f.readlines()
    return [line.strip() for line in lines if not line.startswith("#")]


def is_ignored(path, ignore_patterns):
    for pattern in ignore_patterns:
        if fnmatch.fnmatch(path, pattern):
            return True
    return False
