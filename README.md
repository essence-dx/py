# DX Python Workspace

`G:\Dx\py` is the DX Python workspace. It coordinates CPython acceleration work, package-manager research, benchmark tooling, and lane receipts without flattening every embedded checkout into one giant Git repository.

## Repository Model

- This repo tracks the workspace policy, manifests, benchmark source, and human-readable plans, receipts, and reports.
- `cpython` and `package-manager` are embedded source repositories with their own Git histories.
- `cpython-lane5`, `cpython-upstream-main`, and `worktrees/*` are CPython worktree checkouts with repaired local Git pointer metadata.
- CPython lane worktrees are preserved on their own remote branches; check `manifests/workspace-repositories.json` before merging or deleting them.
- `official-python`, `artifacts/official*`, `artifacts/pycache`, benchmark runs, LLVM payloads, and build outputs are local rebuildable or binary payloads and are intentionally ignored.

## Branch Model

- `main` is the stable release branch.
- `dev` is the active integration branch.
- GitHub Actions are intentionally not added here yet. Use local read-only checks until the Python workspace is ready for a dedicated CI plan.

## First Checks

From this folder:

```powershell
git status -sb
git lfs status
git -C .\cpython status -sb
git -C .\package-manager status -sb
```

Before moving, deleting, or rebuilding anything under this workspace, refresh `manifests/workspace-repositories.json` and confirm whether the target is source, a worktree checkout, or a rebuildable artifact.
