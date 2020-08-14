"""
Indexes IPython Notebook Metadata
"""
import json
import typing
from pathlib import Path


def _read_notebook_file(path: Path) -> dict:
    with path.open(mode="r") as notebook_file:
        return json.load(notebook_file)


def _read_notebook_metadata(path: Path) -> dict:
    return _read_notebook_file(path)["metadata"]


def _apply_inclusion_list(
        source: typing.Dict[typing.AnyStr, typing.Any],
        inclusion_list: typing.Iterable[typing.AnyStr]
) -> dict:
    """
    Copies top-level keys from the source into a new dictionary
    :param source: Any dictionary with string-keys. Value is not mutated.
    :param inclusion_list: Top-level keys to copy into the output.
    :return: The resulting dictionary with specified keys preserved from the input.
    """
    keys_to_include = frozenset(inclusion_list).intersection(source.keys())
    return {key: source[key] for key in keys_to_include}


def _build_metadata_entry(
        notebook_path_relative: Path,
        metadata_keys: typing.Dict[typing.AnyStr, typing.Any],
        inclusion_list: typing.AbstractSet[typing.AnyStr]
) -> typing.Dict[typing.AnyStr, typing.Any]:
    #  Keep only inclusion-listed top-level keys
    metadata_keys = _apply_inclusion_list(metadata_keys, inclusion_list)
    #  Build an entry to be placed in the index
    metadata = {
        "filename": notebook_path_relative.name,
        "name": notebook_path_relative.stem,
        #  as_posix() for forward slashes, to be consistent with Jupyter
        "path": notebook_path_relative.as_posix(),
        #  Notebook-held MetaData is relegated to a sub-path to avoid naming conflicts
        "keys": metadata_keys,
    }
    return metadata


CategoryPath = typing.AnyStr
CategoryMetadataAttributes = typing.Dict[typing.AnyStr, typing.Any]


def process_metadata(
        input_path: Path,
        output_file_stream: typing.TextIO,
        include_keys: typing.Iterable[typing.AnyStr],
        ignore_matching: typing.Iterable[typing.AnyStr],
        category_metadata: typing.Optional[typing.Dict[CategoryPath, CategoryMetadataAttributes]]
) -> None:
    """
    Reads input from IPython notebooks in the given directory path and outputs a JSON aggregate
    :param input_path: Directory to read inputs from (recursively)
    :param output_file_stream: File to which aggregate JSON output will be written
    :param include_keys: Set of top-level MetaData keys from the Notebooks which should be preserved
    :param ignore_matching: Input files where any path "part" matches will be skipped
    :param category_metadata: Input file specifying metadata about categories
    :return: None; output is written as a file.
    """
    include_keys = frozenset(include_keys)
    ignore_matching = frozenset(ignore_matching)
    input_path = input_path.resolve().absolute()
    metadata_list = []
    for notebook_path in input_path.rglob("*.ipynb"):
        relative_path = notebook_path.relative_to(input_path)
        path_parts = relative_path.parts
        if not any(part in path_parts for part in ignore_matching):
            resolved = notebook_path.resolve().absolute()
            notebook_metadata = _read_notebook_metadata(resolved)
            entry = _build_metadata_entry(relative_path, notebook_metadata, include_keys)
            metadata_list.append(entry)

    result = {
        "entries": metadata_list,
        "categories": (category_metadata or {}),
    }

    json.dump(result, output_file_stream, indent=True)


def main(argv: typing.List[typing.AnyStr]) -> None:
    """
    Entrypoint
    :param argv: sys.argv
    :return: None
    """
    import argparse

    argp = argparse.ArgumentParser(
        description="Creates a metadata index for IPython Notebooks",
        add_help=True,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    def existing_dir_path(path_str: str) -> Path:
        path = Path(path_str)
        if not path.is_dir():
            raise argparse.ArgumentTypeError(
                "{} is not a path to a valid, existing directory".format(path_str)
            )
        return path

    def existing_file_path(path_str: str) -> Path:
        path = Path(path_str)
        if not path.is_file():
            raise argparse.ArgumentTypeError(
                "{} is not a path to a valid, existing file".format(path_str)
            )
        return path

    argp.add_argument(
        "input_dir",
        type=existing_dir_path,
        help="Directory path from which to recursively read inputs",
    )
    argp.add_argument(
        "output_file",
        type=argparse.FileType("w", encoding="UTF-8"),
        help="File path into which the program should write outputs; Use '-' for stdout",
    )
    argp.add_argument(
        "--include-keys",
        dest="include_keys",
        help="Top-level metadata keys from the inputs which should be kept",
        nargs="*",
        required=True,
    )
    argp.add_argument(
        "--ignore",
        "--ignore-matching",
        dest="ignore",
        help="Input paths matching any given part will be filtered",
        nargs="+",
        required=False,
        default=[".ipynb_checkpoints"],
    )
    argp.add_argument(
        "--category-metadata",
        dest="category_metadata",
        type=existing_file_path,
        help="Mapping of category IDs (forward slash separated) to category-specific metadata",
        required=False,
        default=None,
    )

    parsed = argp.parse_args(argv[1:])
    process_metadata(
        input_path=parsed.input_dir,
        output_file_stream=parsed.output_file,
        include_keys=parsed.include_keys,
        ignore_matching=parsed.ignore,
        category_metadata=json.loads(Path(parsed.category_metadata).read_text()),
    )


if __name__ == '__main__':
    import sys

    main(sys.argv)
