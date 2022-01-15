from pathlib import Path
from typing import List

from pydantic import BaseModel

from .config import DEFAULT_SOURCE_EXCLUDES
from . import logger


class SourceFinder(BaseModel):
    path: Path
    exlcudes: List[Path] = []
    po_paths: List[Path] = []

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.po_paths = self._exclude(self._get_po_paths())

        length = len(self.po_paths)
        if not length:
            logger.error(f"Cannot found any .po file from '{self.path}'!", err=True)
        else:
            logger.info(f"Found {length} po file(s)")

    def _get_po_paths(self) -> List[Path]:
        """Find all .po files in given path"""
        if not self.path.exists():
            logger.error(f"The path '{self.path.absolute()}' does not exist!", err=True)

        # return 1-element list if it's a file
        if self.path.is_file():
            return [self.path]

        # find all .po files
        po_paths = list(self.path.glob("**/*.po"))
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
