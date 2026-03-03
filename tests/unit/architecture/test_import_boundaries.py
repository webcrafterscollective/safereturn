from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DOMAIN = ROOT / "app" / "domain"
APPLICATION = ROOT / "app" / "application"


FORBIDDEN_IN_DOMAIN = {
    "fastapi",
    "sqlalchemy",
    "starlette",
    "app.infrastructure",
    "app.interfaces",
}

FORBIDDEN_IN_APPLICATION = {
    "fastapi",
    "sqlalchemy",
    "starlette",
    "app.infrastructure",
    "app.interfaces",
}


def _imports_in_file(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                names.add(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module)
    return names


def _assert_layer_is_clean(layer_path: Path, forbidden: set[str]) -> None:
    py_files = [p for p in layer_path.rglob("*.py") if p.name != "__init__.py"]
    assert py_files, f"Expected Python files under {layer_path} to enforce boundaries"

    for file_path in py_files:
        imports = _imports_in_file(file_path)
        for imported in imports:
            for blocked in forbidden:
                assert not (
                    imported == blocked or imported.startswith(f"{blocked}.")
                ), f"{file_path} imports forbidden dependency {imported}"


def test_domain_layer_does_not_depend_on_framework_or_infra() -> None:
    _assert_layer_is_clean(DOMAIN, FORBIDDEN_IN_DOMAIN)


def test_application_layer_does_not_depend_on_framework_or_infra() -> None:
    _assert_layer_is_clean(APPLICATION, FORBIDDEN_IN_APPLICATION)


def test_expected_root_files_exist() -> None:
    assert (ROOT / "app" / "domain" / "errors.py").exists()
    assert (ROOT / "app" / "application" / "errors.py").exists()
