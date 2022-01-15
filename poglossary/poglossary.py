from pathlib import Path
import re
from shutil import get_terminal_size
import textwrap
from typing import Dict, List, NamedTuple, Pattern, Union

import polib
from tabulate import tabulate
import typer

from .config import Config, DEFAULT_SOURCE_PATH, DEFAULT_CONFIG_PATH
from .find_sources import SourceFinder
from . import logger

app = typer.Typer()


class Match(NamedTuple):
    path: Path
    linenum: int
    msgid: str
    msgstr: str
    lost_trans: Dict[str, Union[str, List[str]]]


def check_glossary(
    po_files: List[Path],
    glossary: Dict[str, Union[str, List[str]]],
    ignore_pattern: Pattern,
):
    if not glossary:
        return [], []

    pattern = re.compile(r'\b' + r'\b|\b'.join(glossary.keys()) + r'\b')

    results = []
    errors = []
    for path in po_files:
        try:
            pofile = polib.pofile(path)
        except OSError:
            errors.append(f"{path} doesn't seem to be a .po file")
            continue

        for entry in pofile.translated_entries():
            if not entry.msgstr:
                continue

            # remove the substring with ignore_pattern before matching
            msgid = ignore_pattern.sub("", entry.msgid.lower())
            msgstr = ignore_pattern.sub("", entry.msgstr.lower())

            matched_keys = pattern.findall(msgid)
            if not matched_keys:
                continue

            lost_trans = {}
            for key in set(matched_keys):
                target = glossary[key]
                p = None
                if isinstance(target, str):
                    p = re.compile(target)
                elif isinstance(target, list):
                    p = re.compile('|'.join(target))

                if p and not p.findall(msgstr):
                    lost_trans[key] = target

            if lost_trans:
                colored_msgid = entry.msgid
                for key in lost_trans.keys():
                    colored_msgid = re.sub(
                        key,
                        typer.style(key, fg=typer.colors.RED),
                        colored_msgid,
                    )
                m = Match(path, entry.linenum, colored_msgid,
                          entry.msgstr, lost_trans)
                results.append(m)
    return errors, results


def display(matches: List[Match]) -> None:
    table_value = []
    terminal_size = get_terminal_size()[0]
    for m in matches:
        line_info = f"{typer.style(m.path, fg=typer.colors.MAGENTA)}:" + \
            f"{typer.style(m.linenum, fg=typer.colors.GREEN)}"
        lost_trans_info = ""
        for k, v in m.lost_trans.items():
            lost_trans_info += f"\n{k}: {v}"
        value = [
            line_info + '\n' + textwrap.fill(f"{m.msgid}",
                                             width=int(terminal_size * 0.35)),
            textwrap.fill("\n" + m.msgstr, width=int(terminal_size * 0.17)),
            textwrap.fill(lost_trans_info, width=int(terminal_size * 0.12)),
        ]
        table_value.append(value)
    table = tabulate(
        table_value,
        headers=['msgid', 'msgstr', 'missing'],
        tablefmt="fancy_grid",
    )
    print(table)


@app.command()
def check(
    path: Path = typer.Argument(
        DEFAULT_SOURCE_PATH,
        help="the path of the directory storing .po files",
    ),
    config_file: Path = typer.Argument(
        DEFAULT_CONFIG_PATH,
        help="input mapping file",
    ),
    excludes: List[Path] = typer.Option(
        [],
        help="the directories that need to be omitted",
    ),
):
    """
    poglossary: check translated content in .po files based on given translation mapping
    """
    config = Config(config_file)
    po_paths = SourceFinder(path=path, excludes=excludes).po_paths
    errors, results = check_glossary(
        po_paths,
        config.glossary,
        config.ignore_pattern,
    )

    if errors:
        for error in errors:
            logger.error(error)
        raise typer.Exit(code=1)

    if results:
        display(results)
    else:
        logger.info("No missing translation")
