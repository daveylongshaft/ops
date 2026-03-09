# Prompt: Docstrings — Services and Root Scripts

## Goal

Add full docstrings to undocumented functions in `/opt/csc/services/` and root-level Python scripts.

## Docstring Standard

**The bar: a developer must be able to call any function correctly by reading ONLY its docstring, without ever looking at the implementation.** If the docstring doesn't give you enough to call it right on the first try, it's incomplete.

**Why:** These docstrings are interface contracts, not implementation notes. Any function should be re-implementable in any language or logic model and the system still works — as long as the contract is honored. Document the *what*, not the *how*. The inputs, outputs, data shapes, error behavior, and side effects define the function. The code inside is just one way to satisfy that contract.

**Logic tables:** If a function's behavior can be fully described as a finite input→output mapping (e.g. command name → handler, numeric code → string, mode char → permission), document that mapping exhaustively in the docstring. This lets an implementer replace the logic with a simple lookup table/dict instead of branching code. List every valid input and its corresponding output.

Every docstring MUST include:

1. **Args** — every argument: name, type, valid values/ranges, constraints.
2. **Returns** — exact return type and all possible return values.
3. **Raises** — every exception and under what conditions.
4. **Data** — data structures read/written/mutated, with their shape.
5. **Side effects** — I/O, logging, disk writes, broadcasts.
6. **Thread safety** — if relevant.
7. **Children** — non-trivial functions this calls.
8. **Parents** — what calls this, if known.

```python
def list_directory(self, path="."):
    """
    List files and subdirectories at the given path.

    Args:
        path (str, optional): Directory path to list, relative to server
            working directory. Defaults to ".". Must be a valid readable
            directory. Path traversal (../) is allowed but confined to
            project root by the service sandbox.

    Returns:
        str: Newline-separated listing of directory entries (files and
            subdirs). Returns an error string starting with "Error:"
            if path doesn't exist or isn't readable.

    Raises:
        No exceptions raised — errors are returned as strings.

    Data:
        Reads filesystem via os.listdir(). No internal state mutated.

    Parents:
        Called by service dispatcher when user sends
        `AI <token> dir_lister list_directory [path]`.
    """
```

**Omit sections only if truly not applicable.** When in doubt, include it.

## Items to Document

### services/builtin_service.py (1 item)
- `builtin.__init__` (line 126)

### services/dir_lister_service.py (2 items)
- `dir_lister.__init__` (line 5)
- `dir_lister.list_directory` (line 9)

### generate_tree.py (2 items)
- `generate_tree` (line 6)
- `main` (line 29)

### test_irc_commands.py (2 items)
- `IRCTestClient.__init__` (line 35)
- `IRCCommandTester.__init__` (line 108)

**Total: 7 items**

## Rules

- Do NOT change any code logic — docstrings only
- Read each file before editing
- Use Haiku-tier agents

Verified complete.
