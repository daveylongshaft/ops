# Generic Agent Types

These are examples of simple, focused agents that can be created using the generic agent template. Each has one job and doesn't need complex orchestration.

## 1. Code Reviewer Agent

**Task:** Review code for quality, correctness, security

**Prompt example:**
```markdown
# Review csc-server/server.py

Check for:
- Correctness
- Performance issues
- Security concerns
- Best practices

Output: Written review with issues and suggestions
```

**What they do:**
1. Use tools/INDEX.txt to find Server class
2. Read the implementation
3. Check related files
4. Write review documenting findings
5. Journal each step
6. Exit with COMPLETE

**No need to know:** How git works, how maps refresh, orchestration details

---

## 2. Documentation Generator Agent

**Task:** Generate or update documentation

**Prompt example:**
```markdown
# Generate API documentation for csc-server

Document:
- All public classes and methods
- Parameters and return types
- Examples for key functions

Output: API.md file
```

**What they do:**
1. Use tools/INDEX.txt to find all public APIs
2. Read implementations to understand behavior
3. Generate markdown documentation
4. Create/update docs/API.md
5. Journal steps
6. Exit with COMPLETE

**No need to know:** Where docs will be committed, how the site builds

---

## 3. Code Analyzer Agent

**Task:** Analyze code for specific patterns or issues

**Prompt example:**
```markdown
# Find all places where exceptions are caught but not logged

Analyze:
- All try/except blocks
- Missing logging statements
- Potential silent failures

Output: Report with file locations and suggestions
```

**What they do:**
1. Use p-files.list to find all .py files
2. Read each file looking for patterns
3. Document findings with file:line references
4. Create analysis report
5. Journal findings
6. Exit with COMPLETE

**No need to know:** Version control, build systems

---

## 4. Test Coverage Agent

**Task:** Analyze and improve test coverage

**Prompt example:**
```markdown
# Check test coverage for csc-server

Analyze:
- What's tested
- What's missing
- Critical gaps

Output: Coverage report with recommendations
```

**What they do:**
1. Use tools/INDEX.txt to find all classes/methods
2. Use tests.txt to understand test structure
3. Check test files for coverage
4. Identify gaps
5. Document with recommendations
6. Journal analysis
7. Exit with COMPLETE

**No need to know:** Coverage tools, test runners (wrapper handles that)

---

## 5. Dependency Analyzer Agent

**Task:** Check for unused imports, circular dependencies

**Prompt example:**
```markdown
# Analyze dependencies in csc-server package

Find:
- Unused imports
- Circular dependencies
- External dependencies not in requirements

Output: Dependency analysis report
```

**What they do:**
1. Use p-files.list to find all .py files in csc-server
2. Read each file checking imports
3. Cross-reference with INDEX.txt to see what's used
4. Document findings
5. Journal analysis
6. Exit with COMPLETE

**No need to know:** How package managers work, dependency resolution

---

## 6. Platform Compatibility Analyzer

**Task:** Check code for platform-specific issues

**Prompt example:**
```markdown
# Check csc-server for Windows/Linux compatibility

Analyze:
- Platform-specific imports
- Path handling
- Process management calls

Output: Compatibility report with issues and fixes
```

**What they do:**
1. Use p-files.list to find Python files
2. Read looking for os.path, subprocess, signal, etc.
3. Check against known compatibility issues
4. Document findings with suggestions
5. Journal issues found
6. Exit with COMPLETE

**No need to know:** CI/CD pipelines, test gating (wrapper handles that)

---

## 7. Security Scanner Agent

**Task:** Check for common security issues

**Prompt example:**
```markdown
# Security review of csc-server

Check for:
- Hardcoded secrets
- SQL injection risks
- Insecure deserialization
- Shell injection risks

Output: Security report with severity levels
```

**What they do:**
1. Use p-files.list to find code files
2. Search for dangerous patterns
3. Check config files for secrets
4. Document findings with severity
5. Suggest fixes
6. Journal analysis
7. Exit with COMPLETE

**No need to know:** How security fixes get deployed, approval processes

---

## Generic Agent Creation Template

To create a new generic agent:

1. **Define one clear job:**
   - "Review code"
   - "Generate docs"
   - "Find patterns"
   - "Analyze coverage"

2. **Use code maps:**
   - tools/INDEX.txt for structure
   - p-files.list for file discovery
   - tree.txt for navigation

3. **Do the work:**
   - Read files as needed
   - Analyze or generate output
   - Create/modify files per task

4. **Journal steps:**
   - One echo >> line per action
   - In the prompt file

5. **Exit:**
   - Print COMPLETE
   - Let wrapper handle the rest

---

## Key Principle

**Generic agents are focused workers:**
- They receive a clear task
- They use code maps to understand context
- They do their work
- They journal what they did
- They exit

**They DON'T need to know:**
- Git workflows
- How maps refresh
- How the orchestration system works
- Infrastructure details

The wrapper takes care of all that.
