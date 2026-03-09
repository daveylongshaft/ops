# Prompt: Scrub Co-Authored-By Lines from Git History

## Problem Statement

Approximately 40 commits in the repository contain `Co-Authored-By: Claude ...` trailer lines in their commit messages. Per project policy, AI contributions are logged in `/opt/csc/contrib.txt` only — not in git commit metadata.

## Task

Use `git filter-branch` or `git filter-repo` to rewrite ALL commit messages, removing any line matching:

```
Co-Authored-By: *
```

### Preferred method (git filter-repo)

```bash
pip install git-filter-repo

cd /opt/csc
git filter-repo --message-callback '
import re
return re.sub(rb"\n*Co-Authored-By:.*\n?", b"", message).rstrip() + b"\n"
' --force
```

### Alternative method (git filter-branch)

```bash
cd /opt/csc
git filter-branch --msg-filter '
sed "/^Co-Authored-By:/d" | sed "/^$/N;/^\n$/d"
' --tag-name-filter cat -- --all
```

## Verification

After rewriting:

```bash
# Should return 0
git log --all --format="%B" | grep -ci "co-authored"
```

## Post-Rewrite

- Force push all branches: `git push --force --all`
- Force push tags: `git push --force --tags`
- Notify any collaborators to re-clone or `git pull --rebase`

## Notes

- This is a history rewrite — all commit hashes will change
- Back up the repo before running (`cp -a /opt/csc /opt/csc.bak`)
- This is a one-time cleanup; CLAUDE.md has been updated to prevent future occurrences
