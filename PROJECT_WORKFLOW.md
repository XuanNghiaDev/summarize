# Project Workflow and Checkpointing

This document explains how to create safe checkpoints, feature branches, and rollback procedures for this project.

## Create a checkpoint (Stable release)

1. Ensure the project is working and all tests/manual checks pass.
2. Create/verify `.gitignore` is present (ignore `node_modules`, `venv`, `.env`, etc.).
3. Initialize Git (if not already):

```bash
git init
```

4. Add files and commit the stable state:

```bash
git add .
git commit -m "Stable v1 - summarize + quiz + auth working"
```

5. Tag the commit as stable:

```bash
git tag stable-v1
```

## Feature branch workflow

Before starting a new feature, create a feature branch from `stable-v1`:

```bash
git checkout -b feature/your-feature-name stable-v1
```

Work on the feature, commit regularly:

```bash
git add .
git commit -m "Add: short description of change"
```

If the feature is ready and tested, merge back into main or create a PR targeting `main`.

## Rollback procedures

If a feature breaks things and you need to return to the stable checkpoint:

```bash
git checkout stable-v1
```

Or to reset the current branch to the stable commit (destructive — loses uncommitted changes):

```bash
git reset --hard stable-v1
```

## Recovering after bad AI-generated changes

1. If AI modifications introduced unwanted changes, discard them by checking out the stable tag or commit:

```bash
git checkout stable-v1
```

2. Create a new feature branch from `stable-v1` and re-apply only the safe, reviewed changes.

## Creating subsequent stable versions

When the codebase reaches a new stable point (after QA):

```bash
git add .
git commit -m "Stable v2 - brief description"
git tag stable-v2
```

Repeat for `stable-v3`, etc.

## Backup (manual and automated)

- Manual: run the provided `backup_project.bat` to create a timestamped backup folder excluding `node_modules`, `venv`, and `dist`.
- Automated: integrate `backup_project.bat` into a scheduled task if you want nightly backups.

## Exact git commands summary

```bash
git init
git add .
git commit -m "Stable v1 - summarize + quiz + auth working"
git tag stable-v1
```

## Notes

- Do NOT modify business logic or change APIs as part of checkpointing.
- Keep commits focused and small when possible; tag only truly stable states.
