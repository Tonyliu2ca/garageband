## GarageBand Content Downloader

Downloads the free GarageBand content that is installed on first run.

### Usage:
```
./get_audio_content.py [-h] [-o <folder>] [-l] [-y YYYY]
        -h  Display help
        -p <[garageband | logicpro]>
            Download packages for a specific app. Defaults to
            GarageBand.
        -o <folder>
            Output download to specified folder.
            Folder is created if it does not exist.
            If -o is not supplied, default location is /tmp
        -l  List packages available, as well as file size and total
            size.
        -v  Verbose output
        -y YYYY
            Specify content release year to download that content.

Example:
    ./get_audio_content.py -l -p logicpro -y 2015
```

### License
Licensed under the Creative Commons BY SA license:
- https://creativecommons.org/licenses/by-sa/4.0/

Progress bar implementation courtesy of Fabio Trevisiol
- https://stackoverflow.com/questions/2028517/python-urllib2-progress-hook

### Disclaimer
```
The intent of this tool is to allow a licensed user to trivially download
audio content related to properly licensed versions of Apple software and
the related content downloaded on first run, or after in app purchases are
made.
```
