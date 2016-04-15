## Apple Audio Content Downloader

Downloads additional audio content for Apple products such as GarageBand, and Logic Pro X.

### Usage:
```
./get_audio_content.py [-h] [-o <folder>] [-l] [-y YYYY]
        -h  Display help
        -p <[garageband | logicpro]>
            Download packages for a specific app.
            Defaults to GarageBand if not supplied.
        -o <folder>
            Output download to specified folder.
            Folder is created if it does not exist.
            If -o is not supplied, default location is /tmp
        -l  List packages available, as well as file size and total
            size. If this is NOT supplied, defaults to downloading
            content.
        -v  Verbose output.
        -y YYYY
            Specify content release year to download that content.
            Can be provide multiple years to download.
            If this is not supplied, defaults to all known years.

Example:
    ./get_audio_content.py -l -p logicpro -y 2015
        Lists all Logic Pro X content released in 2015.
    ./get_audio_content.py -y 2013 2015
        Downloads all GarageBand content for 2013, and 2015.
```

### License
Licensed under the Creative Commons BY SA license:
- https://creativecommons.org/licenses/by-sa/4.0/

Progress bar implementation courtesy of Fabio Trevisiol
- https://stackoverflow.com/questions/2028517/python-urllib2-progress-hook

### Disclaimer
This goal in writing this tool is to facilitate the easy retrieval of additional content for various Apple products, such as GarageBand, and Logic Pro X.

Therefore it is up to the end user to ensure they have the correct licensing for content downloaded with this tool.
