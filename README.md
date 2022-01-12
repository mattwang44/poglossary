# poglossary

A CLI tool that scans through translation project (`.po` files) searching for mistranslated terms based on the user-defined glossary mapping.

This project is special tailored for [Python Documentation Translation Project (zh_TW)](https://github.com/python/python-docs-zh-tw) but can be applied for all translation projects that use Portable Object files (`.po`).

## Usage

```yml
# Sample config file (.yml)
glossary:
  exception: 例外
  function: 函式
  instance: 實例
  type: # can be a list of possible translated terms
    - 型別
    - 種類
```

```sh
> python poglossary --help

# Usage: python -m poglossary [OPTIONS] [PATH] [CONFIG_FILE]

#   poglossary: check translated content in .po files based on given translation
#   mapping

# Arguments:
#   [PATH]         the path of the directory storing .po files  [default: .]
#   [CONFIG_FILE]  input mapping file  [default: ./poglossary.yml]

# Options:
#   --excludes PATH       the directories that need to be omitted
#   --install-completion  Install completion for the current shell.
#   --show-completion     Show completion for the current shell, to copy it or
#                         customize the installation.
#   --help                Show this message and exit.
```

```shell
poetry run python3 poglossary <source_path> <config_file>
```

## Sample Output

![image](https://user-images.githubusercontent.com/24987826/149136080-357c673d-41d9-4835-8ed5-f6ef37cf625d.png)

## Todo

- [ ] Functionality
  - [ ] More handy parameters/options
- [ ] CI/CD
  - [ ] Unit tests
  - [ ] Static checks (mypy, isort, etc)
  - [ ] Upload to PyPI
- [ ] Config files
  - [ ] Handle missing fields.
  - [ ] Commands for creating a basic config file.
