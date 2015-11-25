# android-sdk-updater

A tool for keeping Android dependencies up-to-date in an unattended environment. Pass it your `$ANDROID_HOME` and let it
update everything in-place. Optionally, provide a list of package names (from `android list sdk --all`) and bootstrap
your environment.

This tool is especially useful for continuous-integration environments.

## Usage

```
android-sdk-updater <sdk-root> [<package> ...]
```

## License

```
Copyright 2015 Tad Fisher

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```