from pathlib import Path

import pytest

from structfast.exceptions import ParseError
from structfast.parser import parse_structure


def test_parse_unicode_tree() -> None:
    text = """
    a2a-system/
    ├── backend/
    │   ├── agents/
    │   │   ├── planner.py
    │   │   └── worker.py
    │   └── main.py
    └── requirements.txt
    """
    nodes = parse_structure(text)
    assert [(node.name, node.type, node.depth) for node in nodes] == [
        ("a2a-system", "dir", 0),
        ("backend", "dir", 1),
        ("agents", "dir", 2),
        ("planner.py", "file", 3),
        ("worker.py", "file", 3),
        ("main.py", "file", 2),
        ("requirements.txt", "file", 1),
    ]


def test_parse_indentation_based_tree() -> None:
    text = """
    project
        src
            main.py
        README.md
    """
    nodes = parse_structure(text)
    assert [node.depth for node in nodes] == [0, 1, 2, 1]
    assert [node.type for node in nodes] == ["dir", "dir", "file", "file"]


def test_parse_smart_mode_handles_markdown_and_tabs() -> None:
    text = """
    ```text
    project/
    \t- app/
    \t  - __init__.py
    \t  - service.py
    ```
    """
    nodes = parse_structure(text, smart=True)
    assert [(node.name, node.depth) for node in nodes] == [
        ("project", 0),
        ("app", 1),
        ("__init__.py", 2),
        ("service.py", 2),
    ]


def test_parse_invalid_depth_jump_raises() -> None:
    text = """
    root/
            deep.py
    """
    with pytest.raises(ParseError):
        parse_structure(text)


def test_parse_from_file_path(tmp_path: Path) -> None:
    source = tmp_path / "structure.txt"
    source.write_text("root/\n└── file.txt\n", encoding="utf-8")
    nodes = parse_structure(str(source))
    assert nodes[-1].name == "file.txt"


def test_parse_strips_markdown_wrappers_and_inline_comments() -> None:
    text = """
    project1/
    ├── **.env**                       # Environment variables
    ├── **alembic/**                   # Database migrations
    │   ├── versions/
    │   └── env.py
    ├── **app/**
    """
    nodes = parse_structure(text)
    assert [(node.name, node.type, node.depth) for node in nodes] == [
        ("project1", "dir", 0),
        (".env", "file", 1),
        ("alembic", "dir", 1),
        ("versions", "dir", 2),
        ("env.py", "file", 2),
        ("app", "dir", 1),
    ]


def test_parse_handles_partial_markdown_and_or_alternatives() -> None:
    text = """
    project1/
    ├── **__init__**.py
    ├── **requirements.txt** or **pyproject.toml** # Project dependencies/metadata
    └── **data_analyzer_agent/** # Another example agent
    """
    nodes = parse_structure(text)
    assert [(node.name, node.type, node.depth) for node in nodes] == [
        ("project1", "dir", 0),
        ("__init__.py", "file", 1),
        ("requirements.txt", "file", 1),
        ("pyproject.toml", "file", 1),
        ("data_analyzer_agent", "dir", 1),
    ]


def test_parse_keeps_hash_in_real_file_names() -> None:
    text = """
    project/
    â”œâ”€â”€ C#.md
    â””â”€â”€ sprint#1.txt
    """
    nodes = parse_structure(text)
    assert [(node.name, node.type, node.depth) for node in nodes] == [
        ("project", "dir", 0),
        ("C#.md", "file", 1),
        ("sprint#1.txt", "file", 1),
    ]


def test_parse_project_template_with_inline_comments() -> None:
    text = """
    my-random-project/
    â”œâ”€â”€ data/               # Raw and processed data files (if applicable)
    â”œâ”€â”€ docs/               # Project documentation (markdown, diagrams)
    â”œâ”€â”€ src/                # Main source code folder
    â”‚   â”œâ”€â”€ components/     # UI components or logical modules
    â”‚   â”œâ”€â”€ services/       # Business logic
    â”‚   â”œâ”€â”€ utils/          # Helper functions/scripts
    â”‚   â””â”€â”€ main.py         # Entry point of the application
    â”œâ”€â”€ tests/              # Unit and integration tests
    â”œâ”€â”€ config/             # Configuration files
    â”œâ”€â”€ scripts/            # Deployment or maintenance scripts
    â”œâ”€â”€ .gitignore          # Files to exclude from Git
    â”œâ”€â”€ README.md           # Project description and setup instructions
    â”œâ”€â”€ requirements.txt    # Dependencies (or package.json/go.mod)
    â””â”€â”€ Dockerfile          # Containerization file
    """
    nodes = parse_structure(text)
    assert [(node.name, node.type, node.depth) for node in nodes] == [
        ("my-random-project", "dir", 0),
        ("data", "dir", 1),
        ("docs", "dir", 1),
        ("src", "dir", 1),
        ("components", "dir", 2),
        ("services", "dir", 2),
        ("utils", "dir", 2),
        ("main.py", "file", 2),
        ("tests", "dir", 1),
        ("config", "dir", 1),
        ("scripts", "dir", 1),
        (".gitignore", "file", 1),
        ("README.md", "file", 1),
        ("requirements.txt", "file", 1),
        ("Dockerfile", "file", 1),
    ]
