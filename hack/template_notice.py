#!/usr/bin/env python
import argparse
import sys
from pathlib import Path
from typing import Callable, Literal, assert_never

# If you change the header, you'll need to fix it manually in all templated files.
NOTICE_HEADER = "<TEMPLATED FILE!>"
NOTICE_COMMENT = [
    NOTICE_HEADER,
    # Apart from the header, this script can autofix comments when the content changes.
    "This file comes from the templates at https://github.com/konflux-ci/task-repo-shared-ci.",
    "Please consider sending a PR upstream instead of editing the file directly.",
    "See the SHARED-CI.md document in this repo for more details.",
]

SupportedFiletype = Literal["sh", "py", "yaml"]


class UnsupportedFiletype(ValueError):
    pass


def _ensure_notice_comment(filepath: Path) -> None:
    suffix = filepath.suffix.removeprefix(".")
    if suffix not in ("sh", "py", "yaml"):
        raise UnsupportedFiletype(suffix)

    filetype: SupportedFiletype = suffix

    lines = filepath.read_text().splitlines()
    original_lines = lines

    # do a drop -> re-add so that if we change the comment and/or the place
    # where we want it in the files, re-running this script will autofix it
    lines = _drop_notice_comment(lines)
    lines = _add_notice_comment(filetype, lines)

    if lines != original_lines:
        with filepath.open("w") as f:
            f.writelines(line + "\n" for line in lines)


def _drop_notice_comment(lines: list[str]) -> list[str]:
    block_comment_start = None
    block_comment_end = None

    for i, line in enumerate(lines):
        if line.startswith("#") and NOTICE_HEADER in line:
            block_comment_start = i
        elif block_comment_start is not None and not line.startswith("#"):
            block_comment_end = i
            break

    if block_comment_end and not lines[block_comment_end]:
        # also drop the blank line after the comment
        block_comment_end += 1

    result_lines = lines[:block_comment_start]
    if block_comment_end is not None:
        result_lines.extend(lines[block_comment_end:])

    return result_lines


def _add_notice_comment(filetype: SupportedFiletype, lines: list[str]) -> list[str]:
    if not lines:
        return lines

    comment_lines = [f"# {line}" if line else "#" for line in NOTICE_COMMENT]
    comment_lines.append("")  # empty line for readability
    insert_at = None

    match filetype:
        case "sh" | "py":
            first_empty = _first_index(lambda line: not line, lines)
            if first_empty is not None:
                insert_at = first_empty + 1
            else:
                if lines[0].startswith("#!"):
                    comment_lines.insert(0, "")  # separate from the preceding line as well
                    insert_at = 1
                else:
                    insert_at = 0
        case "yaml":
            insert_at = 0
            if lines[0] != "# yamllint disable-file":
                comment_lines = ["# yamllint disable-file", ""] + comment_lines
            elif len(lines) < 2 or lines[1] != "":
                # yamllint comment is already there, add empty line
                comment_lines.insert(0, "")
                insert_at = 1
            else:
                # yamllint comment and empty line are both already there
                insert_at = 2
        case _:
            assert_never(filetype)

    if insert_at is not None:
        return lines[:insert_at] + comment_lines + lines[insert_at:]
    else:
        return lines


def _first_index(pred: Callable[[str], bool], lines: list[str]) -> int | None:
    return next((i for i, line in enumerate(lines) if pred(line)), None)


def fix(template_dir: str) -> None:
    for filepath in Path(template_dir).rglob("*"):
        if filepath.is_dir():
            continue

        try:
            _ensure_notice_comment(filepath)
            msg = "processed file"
        except UnsupportedFiletype as e:
            msg = f"skipping file, unsupported suffix ({e})"

        print(f"{msg}: {filepath}", file=sys.stderr)


def main() -> None:
    parser = argparse.ArgumentParser()
    subcommands = parser.add_subparsers(title="subcommands", required=True)

    fix_command = subcommands.add_parser("fix")
    fix_command.set_defaults(fn=fix)
    fix_command.add_argument("template_dir", default="{{cookiecutter.repo_root}}", nargs="?")

    args = vars(parser.parse_args())

    fn = args.pop("fn")
    fn(**args)


if __name__ == "__main__":
    main()
