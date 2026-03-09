# R40: Refresh Maps and Commit csc-service Package

## Depends: R34

## Task
Run refresh-maps to update the project reference files, then commit the entire
csc-service package.

## Steps

1. Run refresh-maps:
```bash
refresh-maps
```

2. Check that `tools/csc-service.txt` was generated (or create manually if refresh-maps doesn't detect the new package).

3. Stage and commit:
```bash
git add packages/csc-service/
git add tools/
git add tree.txt
git add p-files.list
git commit -m "feat: add csc-service unified package (R01-R39)"
git push
```

## Verification
- `git log -1 --oneline` shows the commit
- `ls tools/csc-service.txt` exists (or similar)
- `git status` is clean


DEAD END - csc-service package already consolidated and operational
