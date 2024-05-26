# imports
import os
import glob
import shutil
import tempfile


# functions
def list_files(
    pattern: str = "*",
    directory: str = os.getcwd(),
    recursive: bool = True,
    include_hidden: bool = False,
) -> list:
    return [
        f
        for f in glob.glob(
            os.path.join(directory, os.path.expanduser(pattern)),
            recursive=recursive,
            include_hidden=include_hidden,
        )
        if os.path.isfile(f)
    ]


def copy_file(src: str, dst: str) -> None:
    shutil.copy(src, dst)


def copy_files(srcs: list[str], dst: str) -> None:
    for src in srcs:
        copy_file(src, dst)


def move_file(src: str, dst: str) -> None:
    shutil.move(src, dst)


def move_files(srcs: list[str], dst: str) -> None:
    for src in srcs:
        move_file(src, dst)


def read_file(file: str) -> str:
    with open(file, "r") as f:
        return f.read()


def read_files(files: list[str]) -> dict[str, str]:
    return {file: read_file(file) for file in files}


def files_to_markdown(files: dict[str, str]) -> str:
    return "\n".join(
        [
            f"### {file}\n\n```python\n{content}\n```"
            if file.endswith(".py")
            else f"### {file}\n\n````{content}````"
            for file, content in files.items()
        ]
    )


def create_temp_dir() -> str:
    return tempfile.mkdtemp()


def write_file(file: str, content: str) -> None:
    with open(file, "w") as f:
        f.write(content)
