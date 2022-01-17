# poglossary

[![Python](https://img.shields.io/pypi/pyversions/poglossary.svg?style=plastic)](https://badge.fury.io/py/poglossary)
[![PyPI](https://badge.fury.io/py/poglossary.svg)](https://badge.fury.io/py/poglossary)

A CLI tool that scans through translation project (`.po` files) searching for mistranslated terms based on the user-defined glossary mapping.

This project is specially tailored for [Python Documentation Translation Project (zh_TW)](https://github.com/python/python-docs-zh-tw) but can be applied for all translation projects that adopt Portable Object files (`.po`).

## Install

To install the current release:

```sh
pip3 install poglossary
```

To update it to the latest version, add `--upgrade` flag to the above commands.

Run `poglossary --help` and you should see the following output if it's installed sucessfully.

```sh
poglossary --help
# Usage: poglossary [OPTIONS] [PATH] [CONFIG_FILE]

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

## Usage

### Config File

A config file in YAML format is required for poglossary, only the following two keys are recognized:

- `glossary` (required): A mapping of untrnaslated term to translated term. The value can be a list if it has multiple translation choices.
- `ignore` (optional): If skipping the checking for specific regex patterns or rST syntax is wanted, add the key `patterns` or `rst_tags` as the example below.

```yml
# Sample config file (.yml)
glossary:
  exception: 例外
  function: 函式
  instance: 實例
  type: # can be a list of possible translated terms of "type"
    - 型別
    - 種類

ignore:
  patterns:
    - "type code(s)?" # "type code" or "type codes" will be skipped
  rst_tags:
    - source # :source:`*` will be skipped
    - class
    - c:
        - func # :c:func:`*` will be skipped
        - data
```

or you can checkout a more detailed configuration in [poglossary.example.yml](./poglossary.example.yml) (, which is the config tend to be used in [pydoc-zhtw](https://github.com/python/python-docs-zh-tw)).

### Command

```shell
poglossary <source_path> <config_file>
```

`poglossary` takes in two optional arguments:

- `source_path`: It can be the path of the target PO file or a directory that stores PO files. Defaults to `.`.
- `config_file`: The path of the config file. Defaults to `./poglossary.yml`.

The sample output is shown below:

![image](https://user-images.githubusercontent.com/24987826/149608253-bec9d2ed-6605-41c8-956c-5e23e8447a5d.png)

## Todo

- [ ] Functionality
  - [ ] More handy parameters/options
- [ ] CI/CD
  - [ ] Unit tests
- [ ] Config files
  - [ ] Handle missing fields.
  - [ ] Commands for creating a basic config file.

## Acknowledge

`poglossary` is primarily inspired by those fantastic translator tools collected in [poutils](https://github.com/afpy/poutils) and [translate toolkit](https://github.com/translate/translate).
