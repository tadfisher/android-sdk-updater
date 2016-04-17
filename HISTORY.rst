.. :changelog:

Change Log
----------

0.0.3 (2016-04-16)
++++++++++++++++++

**Features**

- `--show` lists packages that are `installed`, `available`, and `updates`. Thanks to jules2689 for this feature.

**Bugfixes**

- Handle symlinked SDK install directories. Thanks to jules2689.
- Fix name-mangling for system-image packages. Thanks again to jules2689.
- Blacklist `temp` directories which may be created by newer versions of Android Studio.
- Ignore the `license` property for `platform-tools` packages, which has been removed for release candidates.


0.0.2 (2015-12-17)
++++++++++++++++++

**Bugfixes**

- Handle Unicode strings properly for Python 2.
- Blacklist the NDK package. Plans are in place to support this in a future release.
- Use non-zero exit code when installation of one or more packages fail.

0.0.1 (2015-11-27)
++++++++++++++++++

**Birth**

- Support incremental updates of an SDK installation.
- Support forcing installation of arbitrary SDK packages.
- Read packages from the command line or STDIN.
- Configurable timeouts for package installation.
- Dry-run and verbose output modes for debugging.
