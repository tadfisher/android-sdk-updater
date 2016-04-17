android-sdk-updater
===================

A tool for keeping your Android SDK dependencies up-to-date in unattended environments. Pass it your
:code:`$ANDROID_HOME` and let it update your installed SDK packages as new revisions are released. Optionally, provide a
list of package names (from :code:`android list sdk --all --extended`) to bootstrap your environment, or to ensure your
latest set of dependencies are installed for your next CI run.

This tool is especially useful for continuous-integration servers.

Why do I need this?
-------------------

The command-line tools provided by the SDK are not especially useful for unattended use. Among other problems:

- There is no built-in method to list packages that are already installed. This may be because there is no
  easily-consumed index of installed packages provided, so the SDK manager relies on directory scanning and
  name-mangling. So does this tool, by the way.

- Some packages are unnecessarily downloaded and re-installed with no rhyme or reason when the latest version is already
  installed.

- Some packages are *not* automatically updated when an incremental update is available.

- The package installer requires input from STDIN to actually install packages, because it assumes a human is present to
  accept software licenses.

This tool performs all of the gritty scanning, mangling, parsing, and input-faking necessary to determine:

- Packages you have installed, and their revisions.
- Packages that are available from the official update sites, and their revisions.
- Local packages which should be updated due to an available revision-bump.
- Which packages were actually installed, and which failed to install, after the installer has run.

The ultimate goal of this project is to cease its existence when the Android Tools team addresses these pain points.
These are mostly solved problems in the GUI tool, but they make unattended builds a hassle.

Disclaimer
----------

**By using this tool you acknowledge that associated licenses of the components downloaded are accepted automatically on
your behalf. You are required to have accepted the respective licenses of these components prior to using this tool.**

Requirements
------------

Tested with Python versions 2.7 and 3.5.

Dependencies:

- :code:`jprops`
- :code:`pexpect`
- :code:`semantic_version`

Installing
----------

Using :code:`pip`::

    $ pip install android-sdk-updater

From source::

    $ git clone https://github.com/tadfisher/android-sdk-updater.git
    $ cd android-sdk-updater
    $ python setup.py install

For development::

    $ python setup.py develop

Usage
-----

::

    usage: android-sdk-updater [-h] [-v] [-a ANDROID_HOME] [-d] [-t TIMEOUT] [-vv]
                               [-o ...] [-s {available,installed,updates}]
                               [package [package ...]]

    Update an Android SDK installation

    positional arguments:
      package               name of SDK package to install if not already
                            installed

    optional arguments:
      -h, --help            show this help message and exit
      -v, --version         show program's version number and exit
      -a ANDROID_HOME, --android-home ANDROID_HOME
                            the path to your Android SDK
      -d, --dry-run         compute packages to install but do not install
                            anything
      -t TIMEOUT, --timeout TIMEOUT
                            timeout in seconds for package installation, or 0 to
                            wait indefinitely (default)
      -vv, --verbose        show extra output from android tools
      -o ..., --options ...
                            options to pass to the "android" tool; must be the
                            final option specified
      -s {available,installed,updates}, --show {available,installed,updates}
                            Show available or installed packages

Additional whitespace-delimited :code:`package` arguments can be piped to this tool over the standard input.

Examples
--------

Perform an incremental update of all packages in :code:`$ANDROID_HOME`::

    $ android-sdk-updater

Perform an incremental update of all packages in :code:`/foo/sdk`::

    $ android-sdk-updater --android-home=/foo/sdk

Update all packages in :code:`$ANDROID_HOME` and ensure the installation of packages :code:`android-23` and
:code:`extra-google-google_play_services`::

    $ android-sdk-updater android-23 extra-google-google_play_services

Update all packages in :code:`ANDROID_HOME` and ensure the installation of packages contained in a file::

    $ cat packages.txt
    tools
    platform-tools
    build-tools-23.0.2
    android-23
    addon-google_apis-google-23
    extra-android-m2repository
    extra-google-m2repository
    extra-android-support
    extra-google-google_play_services
    sys-img-x86_64-addon-google_apis-google-23

    $ cat packages.txt | android-sdk-updater

Same as the above, but through a proxy::

    $ cat packages.txt | android-sdk-updater -o --no-https --proxy-host example.com --proxy-port 3218

Show installed packages, available packags, or packages with updates::

    $ android-sdk-updater -s installed

    $ android-sdk-updater -s available
    
    $ android-sdk-updater -s updates

Caveats
-------

The Android NDK is not supported. We plan to support installing and updating the NDK in a future release. In the
meantime, you may see output that includes the following::

    Ignoring 'ndk-bundle' as it is blacklisted.

These warnings may be safely ignored.

License
-------

::

    Copyright 2016 Tad Fisher
    Copyright 2016 Tristan Waddington

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
