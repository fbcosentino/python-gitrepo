## Python GitRepo

GitRepo is a high level pyhton library to handle dependencies inside python projects.

You can specify an URL and an internal folder name, and with one function call you make sure you have that dependency met - it doesn't matter if it was already there or if you have to download it.

In case the folder is already populated with an outdated revision, leaving it as it is or updating it automatically is up to you.

# Dependencies:

This repository also contains the modules git, gitdb and smmap which belong to other authors, but are provided here to ensure GitRepo will be completely portable. 
No installation required: git installed in the OS and a standard python installation will do.

These 3 packages are taken from:

git by Chidi Orji: https://pypi.org/project/python-git/
gitdb by Sebastian Thiel: https://pypi.org/project/gitdb/
smmap by Sebastian Thiel: https://pypi.org/project/smmap/
