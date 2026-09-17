# NotGit

A clone of Git bash written in Python.

## What I Implemented

- Git repository initialization
- Repository structure
- `.git` directory
- `HEAD`
- Git configuration
- Repository discovery
- Basic CLI with `init`

## What I Learned

### Git Repository

A Git repository consists of:
- Working tree
- `.git` directory

### Git Objects

Git stores data as objects:
- Blob
- Tree
- Commit
- Tag

### Object Storage

Git objects are:
1. Serialized
2. Given a SHA-1 hash
3. Compressed with zlib
4. Stored under `.git/objects/`

### Trees

Trees represent directories and point to other
trees and blobs.

### Commits

Commits contain metadata such as:
- tree
- parent
- author
- committer
- commit message

### References

Git references such as:
- HEAD
- branches
- tags

point to commits or other references.

## Limitations

This project is intentionally incomplete.

It does not implement:
- staging area / index
- `add`
- `commit`
- `status`
- complete object resolution
- etc.

The purpose of the project is to understand Git's
internal concepts rather than reproduce Git completely.