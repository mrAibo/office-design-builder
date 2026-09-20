from pathlib import Path
import tomllib


ROOT = Path(__file__).parents[1]


def test_public_package_metadata_is_complete() -> None:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]

    assert project["keywords"]
    assert "Development Status :: 3 - Alpha" in project["classifiers"]
    assert "Programming Language :: Python :: 3.12" in project["classifiers"]
    assert "License :: OSI Approved :: MIT License" in project["classifiers"]
    assert project["urls"]["Homepage"].startswith("https://github.com/")
    assert project["urls"]["Issues"].endswith("/issues")


def test_publish_workflow_builds_checks_and_uses_trusted_publishing() -> None:
    workflow = (ROOT / ".github/workflows/publish.yml").read_text()

    assert "pull_request:" in workflow
    assert "tags:" in workflow
    assert "v*" in workflow
    assert "python -m build --no-isolation" in workflow
    assert "twine check dist/*" in workflow
    assert "actions/upload-artifact@" in workflow
    assert "actions/download-artifact@" in workflow
    assert "environment:" in workflow and "pypi" in workflow
    assert "id-token: write" in workflow
    assert "pypa/gh-action-pypi-publish@release/v1" in workflow
    assert "password:" not in workflow
