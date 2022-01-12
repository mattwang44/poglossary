from pathlib import Path
import re
from typing import Any, Dict, List, Pattern, Union
import pprint as pp

from pydantic import BaseModel, Extra
import typer
import yaml

from utils import log_error, log_info


DEFAULT_SOURCE_PATH = '.'
DEFAULT_SOURCE_EXCLUDES = [
    './.git',
]

DEFAULT_IGNORE_RST_TAG_OBJS = [
    'ref', 'keyword', 'dfn',
]
DEFAULT_IGNORE_PATTERNS = [
    r'{.*?}',
    r'\".*?\"',
    r'``.*?``',
    r'`<.*?>`_',
    r'`.*?`_',
    r'\|.*?\|_',
    r'\*.*?\*',
    r'\*\*.*?\*\*',
]


class SourceSettings(BaseModel):
    path: Path = DEFAULT_SOURCE_PATH
    exlcudes: List[Path] = []
    po_paths: List[Path] = []

    def __init__(self, **data) -> None:
        super().__init__(**data)
        self.po_paths = self._exclude(self._get_po_paths())

        length = len(self.po_paths)
        log_info(f"{length} po files are found from {self.path.resolve()}")

    def _get_po_paths(self) -> List[Path]:
        """Find all .po files in given path"""
        if not self.path.exists():
            log_error(
                f"The path '{self.path.absolute()}' does not exist!")

        # return 1-element list if it's a file
        if self.path.is_file():
            return [self.path]

        # find all .po files
        po_paths = list(self.path.glob("**/*.po"))
        if not len(po_paths):
            log_error(
                f"Cannot found any .po file from '{self.path.resolve()}'!")
        return po_paths

    def _exclude(self, po_paths: List[Path]) -> List[Path]:
        """Exclude paths by the given list of paths"""
        self.exlcudes.extend(DEFAULT_SOURCE_EXCLUDES)

        excluded_files = []
        excluded_dirs = []
        for e in self.exlcudes:
            for path in self.path.glob(e):
                p = path.resolve()
                if p.is_file():
                    excluded_files.append(p)
                else:
                    excluded_dirs.append(p)

        paths = []
        for path in po_paths:
            p = path.resolve()

            # exclude if matched
            if p in excluded_files:
                continue

            # exclude if it's in the given directory
            if any(e in p.parents for e in excluded_dirs):
                continue

            paths.append(path)

        return paths


class IgnoreSettings(BaseModel):
    override_default_patterns: bool = False
    override_default_rst_tags: bool = False
    patterns: List[str] = []
    rst_tags: List[Union[Dict, str]] = []

    class Config:
        extra = Extra.allow

    def __init__(self, **data) -> None:
        super().__init__(**data)
        self.ignore_tags: List[str] = self._build_tags(self.rst_tags)
        self.ignore_pattern: Pattern = self._build_pattern(
            self.patterns, self.ignore_tags)

    def _build_tags(self, tag_objs: List[Union[Dict, str]]) -> List[str]:
        if not self.override_default_rst_tags:
            tag_objs = DEFAULT_IGNORE_RST_TAG_OBJS + tag_objs

        ignore_tags = []

        def _build_tags_recursively(tag_objs, prefix=''):
            for obj in tag_objs:
                if isinstance(obj, str):
                    ignore_tags.append(f":{prefix}{obj}:")
                elif isinstance(obj, dict):
                    for key, vals in obj.items():
                        _build_tags_recursively(vals, prefix + f"{key}:")

        _build_tags_recursively(tag_objs)
        return ignore_tags

    def _build_pattern(self, patterns, ignore_tags=[]) -> Pattern:
        if not self.override_default_patterns:
            patterns = DEFAULT_IGNORE_PATTERNS + patterns

        # append the pattern for matching rst tags
        if ignore_tags:
            patterns.append(f'({"|".join(ignore_tags)})`.*?`')
        return re.compile('|'.join(patterns))


class Config:
    def __init__(
        self,
        config_file: Union[Path, str],
        cmd_path: Path = None,
        cmd_excludes: List[Path] = [],
    ) -> None:
        # TODO: need format check for config file
        config_file_path = Path(config_file)
        self.config: Dict[str, Any] = {}
        if config_file_path.is_file():
            try:
                self.config = yaml.load(
                    config_file_path.open(),
                    Loader=yaml.FullLoader,
                )
            except Exception as err:
                log_error("Something went wrong when loading config file, "
                          f"err={err}")

        self.glossary: Dict[str, Any] = self.config.get('glossary', {})

        cmd = {}
        if cmd_path:
            cmd['path'] = cmd_path
        if cmd_excludes:
            cmd['excludes'] = cmd_excludes
        self.source: SourceSettings = SourceSettings(
            **(self.config.get('source', {}) | cmd),
        )

        self.ignore_settings: IgnoreSettings = IgnoreSettings(
            **self.config.get('ignore', {}),
        )

    @property
    def po_paths(self):
        return self.source.po_paths

    @property
    def ignore_pattern(self):
        return self.ignore_settings.ignore_pattern
