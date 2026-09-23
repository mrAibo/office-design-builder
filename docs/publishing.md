# Publishing to PyPI

Office Design Builder uses PyPI Trusted Publishing. No long-lived PyPI API token is stored in GitHub.

## Current status

The `pypi` GitHub environment and Trusted Publisher were configured for the first release. Verify their identity before each new tag. The current release is v0.2.0 (editable PPTX and DOCX); v0.1.1 remains historical.

## One-time trusted-publisher setup

1. In the GitHub repository, create an environment named `pypi`.
2. Add required reviewers to that environment if manual approval is desired. Do not add a PyPI password or API-token secret.
3. In PyPI's publishing settings, create a pending Trusted Publisher with:
   - PyPI project name: `office-design-builder`
   - GitHub owner: `mrAibo`
   - GitHub repository: `office-design-builder`
   - Workflow filename: `publish.yml`
   - Environment name: `pypi`
4. Confirm that the workflow identity exactly matches those values before approving a release.

PyPI's OIDC exchange requires `id-token: write` only on the publish job. The workflow deliberately grants that permission at job scope and uses `pypa/gh-action-pypi-publish@release/v1` without a password.

## Pre-release checks

From a clean checkout:

```bash
uv sync --frozen --extra dev
rm -rf dist
PIP_NO_INDEX=1 uv run --frozen python -m build --no-isolation
uv run --frozen twine check dist/*
uv run --frozen python -m pytest -q
```

Inspect the wheel and source archive before tagging. Ensure the version in `pyproject.toml` is new: PyPI does not permit replacing an uploaded version.

## Release procedure

Publication is a human-gated operation.

1. Obtain explicit approval to publish the selected version.
2. Confirm the exact release commit is green in the `CI` workflow.
3. Create and push a matching version tag such as `v0.1.1`.
4. Review and approve the protected `pypi` environment deployment, if configured.
5. Verify the `Publish` workflow built and checked the distributions before its publish job used Trusted Publishing.
6. Verify the project page and uploaded filenames on PyPI.
7. Install the exact version from PyPI in a clean Python 3.12 environment.
8. Run `odb --help`, build and verify both the example presentation and DOCX document.

## Rollback and failure handling

PyPI releases are immutable. If an uploaded release is defective, do not reuse its version number. Yank the defective release when appropriate, fix the issue, increment the patch version, repeat all gates, and publish a new version. Never work around Trusted Publishing by adding a long-lived token unless the security model is explicitly reconsidered and approved.
