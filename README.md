## GarageBand Content Downloader

Downloads the free GarageBand content that is installed on first run.

### Usage:
```
./get_gb_content.py [-h] [-o <folder>] [-l] [-y YYYY]
        -h          Display help
        -o <folder> Output download to specified folder.
                    Folder is created if it does not exist.
                    If -o is not supplied, default location is /tmp
        -l          List downloads available
        -y YYYY     Specify content release year to download that content
```
Licensed under the Creative Commons BY SA license:

https://creativecommons.org/licenses/by-sa/4.0/


### Known issues:
- v1.0.3b
    - If an output folder is supplied, the clean up routine won't delete the output folder, only the contents.
    - If the file_test() method can't get remote package file size, then the package will be downloaded again even if it had previously been downloaded.
