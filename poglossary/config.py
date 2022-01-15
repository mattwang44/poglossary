from pathlib import Path
import re
from typing import Any, Dict, List, Pattern, Union

from pydantic import BaseModel, Extra
import yaml

from . import logger


DEFAULT_CONFIG_PATH = "./poglossary.yml"
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
                logger.error("Something went wrong when loading config file, "
                             f"err={err}")

        self.glossary: Dict[str, Any] = self.config.get('glossary', {})

        self.ignore_settings: IgnoreSettings = IgnoreSettings(
            **self.config.get('ignore', {}),
        )

    @property
    def ignore_pattern(self):
        # merely a shorthand
        return self.ignore_settings.ignore_pattern
