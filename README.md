# NotGit

A minimal implementation of Git written in Python, built to understand how Git works internally.

NotGit writes the **same on-disk format as real Git**, so repositories it creates can be read by `git`, and it can read repositories created by `git` (as long as they're not packed).

## Usage

```bash
./NotGit init myrepo
cd myrepo
echo "hello" > hello.txt
../NotGit add hello.txt
../NotGit commit -m "first commit"
../NotGit log | dot -Tpng -o log.png   # commit graph via Graphviz
```

## Implemented Commands

| Command | Description |
|---|---|
| `init` | Create an empty repository |
| `cat-file` | Print the contents of an object |
| `hash-object` | Compute an object's SHA-1 and optionally store it |
| `log` | Print commit history as a Graphviz graph |
| `ls-tree` | List the contents of a tree object |
| `checkout` | Check out a commit into an empty directory |
| `show-ref` | List references |
| `tag` | Create or list tags (lightweight and annotated) |
| `rev-parse` | Resolve a name (branch, tag, short hash) to an object |
| `ls-files` | List files in the index (staging area) |
| `check-ignore` | Check paths against `.gitignore` rules |
| `status` | Show the working tree status |
| `add` | Add files to the index |
| `rm` | Remove files from the working tree and index |
| `commit` | Record the index as a new commit |

## How Git Works (What I Learned)

### The Repository

A repository is a **working tree** (your files) plus a **`.git` directory**, which holds all history, refs, config, and the index.

### Objects and Content Addressing

Git stores everything as objects, and there are four types:

- **Blob**: file contents
- **Tree**: a directory listing that points to blobs and other trees
- **Commit**: points to a tree, parent commit(s), author, committer, and message
- **Tag**: an annotated, named pointer to another object

Each object is:
1. Serialized as `<type> <size>\0<content>`
2. Hashed with SHA-1, and that hash becomes its name
3. Compressed with zlib
4. Stored at `.git/objects/<first 2 hex chars>/<remaining 38>`

Because an object's name *is* the hash of its content, identical content is stored only once, and any corruption is detectable.

### The Merkle DAG

Git's history is a **Merkle DAG** (Directed Acyclic Graph):

```
  commit C3 ──parent──> commit C2 ──parent──> commit C1
     │                     │                     │
    tree                  tree                  tree
   /    \                /    \                   │
 blob   tree  (shared) blob   tree              blob
          │                     │
         blob                  blob
```

- **Merkle**: every object's hash includes the hashes of the objects it points to. A tree hashes its children, and a commit hashes its tree and its parents. Changing a single byte in one file changes that blob's hash, which changes every tree above it, which changes the commit hash. A commit hash therefore **fingerprints the entire history** behind it.
- **DAG**: commits point backward to their parents (a merge has two or more), and a cycle is impossible because a parent must exist before its child's hash can be computed.
- **Structural sharing**: unchanged files and directories keep the same hash, so new commits reuse existing objects instead of copying them.

This is why Git can verify integrity cheaply, compare two trees fast (equal hashes mean identical subtrees, so they can be skipped), and deduplicate storage for free.

### References

Refs are human-friendly names for hashes. They are plain text files under `.git/refs/`:

- **Branches** (`refs/heads/*`) are movable pointers to commits
- **Tags** (`refs/tags/*`) are fixed pointers
- **`HEAD`** usually points to a branch (`ref: refs/heads/main`); when it points to a commit hash instead, HEAD is "detached"

### The Index (Staging Area)

`.git/index` is a binary file listing every tracked path along with its blob hash, mode, and file stat info. `add` writes blobs and updates the index. `commit` builds trees from the index and creates a commit. `status` compares HEAD ↔ index ↔ working tree.

### Ignore Rules

`.gitignore` files are scoped to their directory, and `.git/info/exclude` plus the global config apply to the whole repository. Later rules override earlier ones, and `!` negates a rule.

## Limitations

This project is intentionally incomplete. It does not implement:

- Packfiles (it can't read most cloned repositories)
- Network operations (`clone`, `fetch`, `push`)
- `branch`, `merge`, `diff`, `rebase`
- Checkout into a non-empty directory

## Credits

Based on [Write Yourself a Git](https://wyag.thb.lt/).
