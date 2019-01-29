"""
====================================================
GitRepo
====================================================

High level library to work with Git repositories 
when no developing interaction is needed
I.e. making sure we use most recent version of some
external dependencies

After importing this module, set the repository base
folder using the _REPOS_DIR module property.

:Example:

>>> import gitrepo
>>> gitrepo._REPOS_DIR = 'folder_inside_working_dir/subfolder'
>>> gitrepo._REPOS_DIR = '/var/repos'


>>> my_repo = gitrepo.GitRepo('http://bitbucket.org/fbcosentino/python-gitrepo.git', 'folder/gitrepo')
>>> my_repo.Exists()
False
>>> my_repo.Update()
<git.Repo "<...>\folder_inside_working_dir\subfolder\folder\gitrepo\.git">
>>> my_repo.Exists()
True
>>> my_repo.IsOutdated()
False
>>> my_repo.IsLastLocal()
True
>>> commit_list = my_repo.ListCommits(False) # False argument to get a list
>>> first_commit = commit_list[0]
>>> first_commit_object = first_commit[3]
>>> my_repo.UseRev(first_commit_object)
<git.HEAD "HEAD">
>>> my_repo.IsOutdated()
True
>>> my_repo.IsLastLocal()
True
>>> my_repo.Update()
[<git.remote.FetchInfo object at 0x02970D50>]
>>> my_repo.IsOutdated()
False


:Author:
    Fernando Cosentino
    https://bitbucket.org/fbcosentino/python-gitrepo/
"""


# This is the local directory (relative to the current working directory)
# where the individual repo folders are
# You can also use absolute path
# E.g. _REPOS_DIR = 'repos' means a repository named 'foo'  will be at './repos/foo/.git'
# Or keep it blank to have all your repo folders relative to the project main folder
_REPOS_DIR = ''

# You can always change this at application level, as example below:
#     import gitrepo
#     gitrepo._REPOS_DIR = 'my_repositories'
# But do this BEFORE creating the repo objects (instancing the GitRepo class)


# =================================================
# Basic imports
import time
from datetime import datetime
import os
import sys

# Add the 'lib' subfolder to be able to import modules from there
sys.path.append( os.path.join( os.path.dirname(__file__), 'lib') )

# The 3 import items below must be together and in this exact order, in order to be portable
import smmap # required for gitdb
import gitdb # required for git
import git   # git abstractions

# End of imports
# =================================================

class GitRepo:
    """The GitRepo class encapsulates the work on one specific repository.
    Create one instance of this class for each repository you have.
    
    
    Member Properties:
        :Repo:         The repository internal object from python-git library.
                    None if the repository is not yet present in local folder.
        :RepoUrl:     The URL this repository is associated with.
        :FolderName: The folder_name argument from the constructor.
        :LocalPath:    The local directory where this repository lives in. May not exist yet.
    """

    # Constructor
    def __init__(self, url, folder_name):
        """Constructor takes the repository URL and the local folder 
        where the files are to be stored. They are relative to the
        working directory set in _REPOS_DIR
        
        If the supplied folder is a git repository, information will 
        be fetched from it. Otherwise Repo will be None
        
        :param url: The remote URL
        :param folder_name: The local folder (relative to _REPOS_DIR) to store the repository files
        """
    
        self.RepoUrl = url
        self.FolderName = folder_name
        self.LocalPath = os.path.join(_REPOS_DIR,folder_name)
        if self.Exists():
            try:
                self.Repo = git.Repo(self.LocalPath)
                self.RepoUrl = list(self.Repo.remotes.origin.urls)[0]
            except:
                self.Repo = None
                self.RepoUrl = url
        else:
            self.Repo = None


    def Exists(self):
        """Checkes whether the local folder is already populated with 
        some revision of the remote repository. 
        
        This implementation just checks if the local folder has a .git subfolder.
        
        :returns: True if the local folder is a populated git repository, False otherwise."""
    
        return os.path.exists(  os.path.join(self.LocalPath, '.git')  )
        
    def Clone(self):
        """Used internally by Update(). Avoid calling this method manually.
        
        Clones the remote repository into the local folder, if the local folder is not yet populated.
        
        :returns: The Repo object on success, False if it is already populated, 
                    None if fetching was not possible (such as invalid URL).
        """
    
        if self.Repo is not None:
            return False
        if self.Exists():
            return False
        try:
            repo = git.Repo.clone_from(self.RepoUrl, self.LocalPath)
            self.Repo = repo
        except:
            self.Repo = None
        return self.Repo

    def Pull(self):
        """Used internally by Update(). Avoid calling this method manually.
        
        If the local folder is populated, pulls the most recent revision from remote repository.
        
        :returns: Result of git pull() on success, False if the repository is not yet cloned."""
    
        if self.Repo is None:
            return False
        if self.Exists():
            return self.Repo.remotes.origin.pull()
        else:
            return False

    def Update(self):
        """Clones or updates the local folder matching the most recent revision in the remote repository.
        
        If the local folder is not yet populated, this method invokes Clone(). Otherwise, invokes Pull().
        
        You should always use this method whenever you want the last revision, since
        it is safe to be called regardless of the local folder situation.
        
        :returns: The Repo object on success, False on local folder errors, None on URL errors.
        """
    
        if self.Exists():
            if self.Repo is None:
                return False # something really awkward happened
            else:
                return self.Pull()
        else:
            return self.Clone()
        
    def CurrentRev(self):
        """Provides information on the current local revision commit.
        
        The returned value is a tuple containing:
        * Hex representation of SHA1 hash associated with this commit
        * The committed datetime as an integer inside a string in UNIX epoch system
        * The commit message as string
        * The python-git commit object itself
        
        :returns: Tuple: (hexsha, committed_date, message, commit), 
                    or False if this Repo is not yet cloned
        """
    
        if self.Repo is None:
            return False
        commit = self.Repo.commit()
        # commit.hexsha
        # commit.message
        # commit.name_rev 
        # commit.committed_date 
        #ts = datetime.utcfromtimestamp(commit.committed_date)
        return (commit.hexsha, commit.committed_date, commit.message, commit)
        
    def RemoteRev(self):
        """Provides information on the most recent remote revision commit.
        
        The returned value is a tuple containing:
        * Hex representation of SHA1 hash associated with this commit
        * The committed datetime as an integer a string in UNIX epoch system
        * The commit message as string
        * The python-git commit object itself
        
        :returns: Tuple: (hexsha, committed_date, message, commit),
                    False if this Repo is not yet cloned,
                    or None for connection errors
        """
        if self.Repo is None:
            return False
        try:
            f = self.Repo.remotes.origin.fetch()
            commit = f[0].commit
            return (commit.hexsha, commit.committed_date, commit.message, commit)
        except:
            return None
            
    def LastLocalRev(self):
        """Provides information on the most recent local revision commit.
        This may not be the same as CurrentRev(), since the local copy
        may have been reset to a previous revision after updating.
        
        The returned value is a tuple containing:
        * Hex representation of SHA1 hash associated with this commit
        * The committed datetime as an integer a string in UNIX epoch system
        * The commit message as string
        * The python-git commit object itself
        
        :returns: Tuple: (hexsha, committed_date, message, commit),
                    False if this Repo is not yet cloned,
                    or None if no commits are found in local copy
        """
    
        if self.Repo is None:
            return False
        
        clist = self.ListCommits(False)
        clen = len(clist)
        if clen <= 0:
            return None
        return clist[ clen-1 ]
        
    def CountLocalRevs(self):
        """Returns the number of revisions (commits) the local copy has, i.e. already fetched.
        
        E.g. if a remote repository had 4 revisions when the local copy was last updated,
        a new (5th) commit was made to the remote repository by someone else, and
        the local copy was reset to revision 2, this function will still return 4.
        
        :returns: Integer number of local commits available.
        """
    
        if self.Repo is None:
            return False
        if len(self.Repo.heads) == 0:
            return 0
        revlist = list( self.Repo.iter_commits() )
        return len(revlist)
        
    def IsOutdated(self):
        """Checks if the local working copy is outdated.
        
        Fetches the most recent commit from the remote repository and compares the
        timestamp to the timestamp in current local commit. 
        Returns True if the remote timestamp is newer.
        
        :returns: True if the local copy is not the most recent, False otherwise.
        """
        if self.Repo is None:
            return False
        local_commit = self.CurrentRev()
        remote_commit = self.RemoteRev()
        if remote_commit[1] > local_commit[1]:
            return True
        else:
            return False
            
    def IsLastLocal(self):
        """Checks if the current working revision is the most recent fetched (downloaded) revision.
        
        :returns: True if working with the last local revision, False if the local copy was 
                reset to a previous commit after updating.
        """
    
        if self.Repo is None:
            return False
        local_commit = self.CurrentRev()
        last_commit = self.LastLocalRev()
        if last_commit[0] == local_commit[0]:
            return True
        else:
            return False
        
    def ListCommits(self, assoc=True):
        """Returns a list or dictionary of commits available locally. 
        
        This method is not aware of any changes happening in the remote repository.
        
        Each item in the list/dictionary is a tuple refering to a specific commit, containing:
        * Hex representation of SHA1 hash associated with this commit
        * The committed datetime as an integer a string in UNIX epoch system
        * The commit message as string
        * The python-git commit object itself
        
        If a dictionary is returned, the keys are the timestamp integers (not as strings).
        
        In any case, the order is ascending chronological order (oldest first).
        
        :param assoc: if True, returns dictionary, otherwise returns list
        :returns: list or dictionary, where each item is Tuple: (hexsha, committed_date, message, commit)
        
        """
    
        if self.Repo is None:
            return False
        cs = {}
        for commit in self.Repo.iter_commits():
            cs[int(commit.committed_date)] = (commit.hexsha, commit.committed_date, commit.message, commit)
            # ensure we have ascending time order
        keylist = cs.keys()
        keylist.sort()
        if assoc is True:
            res = {}
            for ek in keylist:
                res[ek] = cs[ek]
        else:
            res = []
            for ek in keylist:
                res.append(cs[ek])
        return res
        
    def UseRev(self, commit):
        """Resets the local copy to the specified commit.
        
        The commit object is the 4th element in the tuples returned by 
            CurrentRev(), LastLocalRev() and the items in the
            list/dictionary returned by ListCommits()
        
        Do not use the commit returned by RemoteRev() since it's not yet downloaded.
        To use the last remote revision, use Update() instead.
        
        To use a revision which is not the last remote one, but is newer than the last
        local one, you must Update() first to download everything and move
        to the last revision, and then use UseRev() to move back to te desired one.
        
        :param commit: The commit object respective to the desired revision
        :returns: Repo on success, False on errors or if the local repository is not cloned
            
        """
    
        if self.Repo is None:
            return False
        try:
            res = self.Repo.head.reset(commit, index=True, working_tree=True)
            return res
        except Exception as e:
            print e
            return False