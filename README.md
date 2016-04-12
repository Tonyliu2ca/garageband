## GarageBand Content Downloader

Downloads the free GarageBand content that is installed on first run.

### Usage:
```
./get_gb_content.py [-h] [-o <folder>] [-l] [-y YYYY]
        -h          Display help
        -o <folder> Output download to specified folder.
                    Folder is created if it does not exist.
                    Defaults to /tmp
        -l          List downloads available
        -y YYYY     Specify content release year to download that content
```
Licensed under the Creative Commons BY SA license:

https://creativecommons.org/licenses/by-sa/4.0/


### Known issues:
- Remote file size is pulled from the plist, this is not always the correct filesize.
- As per above, progress bar may exceed 100% or not quite reach 100%.
