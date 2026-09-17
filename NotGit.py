import argparse
import configparser
from datetime import date

try:
    import grp, pwd
except ModuleNotFoundError:
    pass

from fnmatch import fnmatch
import hashlib
from math import ceil
import os
import re
import sys
import zlib

# ==========================
# Abstract
# ==========================



class GitRepository(object):
    """A git repository"""

    worktree = None
    gitdir = None
    conf = None

    def __init__(self, path, force=False):
        self.worktree = path
        self.gitdir = os.path.join(path, ".git")

        if not (force or os.path.isdir(self.gitdir)):
            raise Exception(f"{path} is not a Git repository")

        self.conf = configparser.ConfigParser()

        cf = repo_file(self, "config")

        if cf and os.path.exists(cf):
            self.conf.read([cf])
        elif not force:
            raise Exception("Configuration file missing")

        if not force:
            vers = int(self.conf.get("core", "repositoryformatversion"))

            if vers != 0:
                raise Exception(
                    f"Unsupported repositoryformatversion: {vers}"
                )


class GitObject(object):
    def __init__(self,data=None):
        if data != None:
            self.deserialize(data)
        else:
            self.init()    

    def serialize(self,repo):
        raise Exception("Not implemneted")
    def deserialize(self,data):
        raise Exception("Not implemneted")

    def init(self):
        pass         

class GitBlob(GitObject):
    fmt = b'blob'
    def serialize(self):
        return self.blobdata
    def deserialize(self,data):
        self.blobdata=data

############################

def repo_path(repo, *path):
    """Return a path under the repository's .git directory."""
    return os.path.join(repo.gitdir, *path)


def repo_dir(repo, *path, mkdir=False):
    """Same as repo_path, but create the directory if needed."""

    path = repo_path(repo, *path)

    if os.path.exists(path):
        if os.path.isdir(path):
            return path
        else:
            raise Exception(f"Not a directory {path}")

    if mkdir:
        os.makedirs(path)
        return path

    return None


def repo_file(repo, *path, mkdir=False):
    """
    Same as repo_path, but make sure the directory
    containing the file exists.
    """

    if repo_dir(repo, *path[:-1], mkdir=mkdir):
        return repo_path(repo, *path)


def repo_create(path):
    """Create a new Git repository at path."""

    repo = GitRepository(path, True)

    if os.path.exists(repo.worktree):

        if not os.path.isdir(repo.worktree):
            raise Exception(f"{path} is not a directory.")

        if os.path.exists(repo.gitdir) and os.listdir(repo.gitdir):
            raise Exception(f"{path} is not empty.")

    else:
        os.makedirs(repo.worktree)

    assert repo_dir(repo, "branches", mkdir=True)
    assert repo_dir(repo, "objects", mkdir=True)
    assert repo_dir(repo, "refs", "tags", mkdir=True)
    assert repo_dir(repo, "refs", "heads", mkdir=True)

    with open(repo_file(repo, "description"), "w") as f:
        f.write(
            "Unnamed repository; edit this file "
            "'description' to name the repository.\n"
        )

    with open(repo_file(repo, "HEAD"), "w") as f:
        f.write("ref: refs/heads/master\n")

    with open(repo_file(repo, "config"), "w") as f:
        config = repo_default_config()
        config.write(f)

    return repo


def repo_default_config():
    ret = configparser.ConfigParser()

    ret.add_section("core")
    ret.set("core", "repositoryformatversion", "0")
    ret.set("core", "filemode", "false")
    ret.set("core", "bare", "false")

    return ret


def repo_find(path=".", required=True):
    """Find the nearest Git repository."""

    path = os.path.realpath(path)

    if os.path.isdir(os.path.join(path, ".git")):
        return GitRepository(path)

    parent = os.path.realpath(os.path.join(path, ".."))

    if parent == path:

        if required:
            raise Exception("No git directory.")
        else:
            return None

    return repo_find(parent, required)

def object_read(repo,sha):
    #Return the object that have this SHA from the repo
    path = repo_file(repo,"objects",sha[0:2],sha[2:])
    if not os.path.isfile(path):
        return None
    with open(path,"rb") as f:
        raw = zlib.decompress(f.read())
        #raw now have bytes
        #b is python syntax means that: anything between ' ' is bytes
        x = raw.find(b' ')  #finds first sapce
        fmt= raw[0:x]   #return the header

        y=raw.find(b'\x00',x) #find null space after x, returns its position
        size = int(raw[x:y].decode("ascii")) #decode return a string
        if size != len(raw)-y-1: #-1 points to the position of the null itself.
            raise Exception(f"Malformed object {sha}: bad length")

        match fmt:
            case b'commit' : c=GitCommit
            case b'tree'   : c=GitTree
            case b'tag'    : c=GitTag
            case b'blob'   : c=GitBlob
            case _:
                raise Exception(f"Unknown type {fmt.decode('ascii')} for object {sha}")

        # Call constructor and return object
        return c(raw[y+1:])

def object_write(obj, repo=None):
    # Serialize object data
    data = obj.serialize()
    # Add header
    result = obj.fmt + b' ' + str(len(data)).encode() + b'\x00' + data
    # Compute hash
    sha = hashlib.sha1(result).hexdigest()

    if repo:
        # Compute path
        path=repo_file(repo, "objects", sha[0:2], sha[2:], mkdir=True)

        if not os.path.exists(path):
            with open(path, 'wb') as f:
                # Compress and write
                f.write(zlib.compress(result))
    return sha    




# =========================
# CLI
# =========================

argparser = argparse.ArgumentParser(
    description="NotGitShell:P"
)

argsubparsers = argparser.add_subparsers(
    title="Commands",
    dest="command"
)


# Git init

argsp = argsubparsers.add_parser(
    "init",
    help="Initialize a new, empty repository."
)

argsp.add_argument(
    "path",
    metavar="directory",
    nargs="?",
    default=".",
    help="Where to create the repository."
)

###########################
#Brigde
###########################
def cmd_init(args):
    repo_create(args.path)





# =========
# Main
# =========
def main(argv=sys.argv[1:]):

    args = argparser.parse_args(argv)

    match args.command:

        case "init":
            cmd_init(args)

        # case "add":
        #     cmd_add(args)

        # case "commit":
        #     cmd_commit(args)

        # case "status":
        #     cmd_status(args)

        # case _:
        #     print("Bad Command.")


if __name__ == "__main__":
    main()