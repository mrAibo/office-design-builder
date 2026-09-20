from pathlib import Path


WORKFLOW = Path(".github/workflows/ci.yml")


def test_ci_workflow_covers_linux_and_windows_python_312() -> None:
    workflow = WORKFLOW.read_text()

    assert "ubuntu-latest" in workflow
    assert "windows-latest" in workflow
    assert 'python-version: ["3.12"]' in workflow
    assert "astral-sh/setup-uv@" in workflow
    assert "uv sync --frozen --extra dev" in workflow
    assert "uv run --frozen python -m pytest -q" in workflow
    assert "uv run --frozen python -m build --no-isolation" in workflow
    assert "uv run --frozen python -m office_design_builder.cli --help" in workflow
