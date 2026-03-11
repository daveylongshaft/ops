# platform_11: GitHub Repo Investigation & Comparison

**Objective:** Investigate your GitHub repositories to find the original `syscmdr` system and create a comparison summary showing evolution from origin to today.

**Depends on:** platform_10 (batch platform work complete)
**Time:** ~90 minutes | **Difficulty:** Research/Analysis | **Next:** platform_12

---

## Task

1. **Search GitHub** for repositories related to syscmdr/CSC
   - Look for: `syscmdr`, `system-commander`, `irc-server`, similar
   - Identify: original repos vs current CSC repo
   - Note: commit history, timestamps, language, architecture

2. **Create comparison summary** (`.md` file)
   - Original syscmdr repo(s): What was the design?
   - CSC repo: What is it now?
   - Side-by-side comparison: architecture, features, tech stack

3. **Gather data** for evolution analysis:
   - GitHub commit history (both repos)
   - contrib.txt (if exists in both)
   - README files
   - Key architectural documents
   - File/code statistics

---

## Execution Steps

### Step 1: GitHub Search

Use GitHub CLI (`gh`) to find repos:

```bash
# List all your repos
gh repo list --limit 100

# Search for specific keywords
gh search repos --owner:<your-github-username> --language:python | grep -i "syscmdr\|irc\|commander"

# For each candidate repo, get details
gh repo view <owner>/<repo> --json description,url,createdAt,pushedAt,languages
```

### Step 2: Analyze Original Repo

Clone or examine the original syscmdr repo:

```bash
# Clone if not already present
git clone https://github.com/<owner>/syscmdr.git /tmp/syscmdr

# Get commit count
cd /tmp/syscmdr && git log --oneline | wc -l

# Get commit history (last 20)
git log --oneline -20

# Check for evolution docs
find . -name "EVOLUTION*" -o -name "HISTORY*" -o -name "CHANGELOG*"

# Count files by type
find . -type f | sed 's/.*\.//' | sort | uniq -c | sort -rn | head -20

# Get architecture overview
ls -la && find . -name "README*" -o -name "ARCHITECTURE*" -o -name "DESIGN*"
```

### Step 3: Compare with Current CSC

```bash
# CSC repo statistics
cd /c/csc
git log --oneline | wc -l  # Total commits
git log --oneline -20  # Recent commits
find packages -name "*.py" | wc -l  # Python files
du -sh packages/*  # Size breakdown
```

### Step 4: Create Comparison Summary

Document in `GITHUB_COMPARISON.md`:

```markdown
# GitHub Repository Comparison

## Original System (syscmdr)

**Repository:** [link]
**Created:** [date]
**Last Updated:** [date]
**Language:** [primary language]
**Total Commits:** [N]

### Architecture
- [Key components from original]
- [Original design patterns]
- [Original goals/purpose]

### Statistics
- Total files: N
- Key modules: [list]
- Dependencies: [key libs]

### Notable Features
- [Original features]
- [Unique capabilities]

## Current System (CSC)

**Repository:** https://github.com/[user]/csc
**Created:** [date]
**Last Updated:** [date]
**Language:** Python 3.8+
**Total Commits:** [N]

### Architecture
- [Current components]
- [Current design patterns]
- [Current goals/purpose]

### Statistics
- Total files: N
- Key modules: [list]
- Dependencies: [current libs]

### Notable Features
- [Current features]
- [Unique capabilities]

## Comparison Table

| Aspect | Original (syscmdr) | Current (CSC) |
|--------|---|---|
| **Core Purpose** | [original] | [current] |
| **Language** | [old] | [new] |
| **Architecture** | [old] | [new] |
| **Key Components** | [old] | [new] |
| **Client Types** | [old] | [new] |
| **Protocol** | [old] | [new] |
| **Storage** | [old] | [new] |
| **Extensibility** | [old] | [new] |

## What Changed (Mutations)

### Removed
- [Features no longer present]

### Added
- [New features]

### Evolved
- [Features that changed significantly]

### Preserved
- [Core concepts still present]

## Analysis Summary

[1-2 paragraph summary of evolution]
```

---

## Data to Collect

**From GitHub CLI:**
```bash
# Get full repo info
gh repo view <owner>/<repo> --json name,description,url,createdAt,pushedAt,defaultBranch,diskUsage,languages,stargazerCount,forkCount

# Get contributor stats
gh repo view <owner>/<repo> --json contributors
```

**From git history:**
```bash
# Commits per author
git shortlog -sn

# File history (find major changes)
git log --name-status --oneline | head -50

# Lines of code over time (rough)
git log --shortstat | grep "files changed" | awk '{insertions+=$4; deletions+=$6} END {print "Total insertions: " insertions " deletions: " deletions}'
```

**From codebase:**
```bash
# Architecture overview
find . -name "*.md" -exec grep -l "architecture\|architecture\|design" {} \;

# Check contrib.txt
cat contrib.txt 2>/dev/null || echo "Not found"
```

---

## Output Files

Create in `/c/csc/docs/`:

1. **GITHUB_COMPARISON.md** — Side-by-side comparison
2. **REPO_STATS.json** — Raw statistics (for programmatic use)
3. **TIMELINE.md** — Evolution timeline (original → current)

---

## Verification Checklist

- [ ] Found original syscmdr repo on GitHub
- [ ] Identified all related repos
- [ ] Gathered commit history from both repos
- [ ] Created GITHUB_COMPARISON.md with full comparison
- [ ] Documented what changed (removed/added/evolved)
- [ ] Collected statistics (commits, files, languages)
- [ ] Found/checked contrib.txt in both repos
- [ ] Noted key architectural differences
- [ ] All data accurate and sourced

---

## Commit

```
research: GitHub repo investigation and comparison

- Identified original syscmdr repository
- Created GITHUB_COMPARISON.md with side-by-side analysis
- Documented mutations: removed/added/evolved features
- Collected commit history and contributor data
- Set foundation for evolution.md analysis

Files:
  - docs/GITHUB_COMPARISON.md
  - docs/REPO_STATS.json
  - docs/TIMELINE.md
```

