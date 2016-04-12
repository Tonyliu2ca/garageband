#!/usr/bin/python
'''Downloads the free GarageBand content that is installed on first run.
Usage:
    ./get_gb_content.py [-h] [-o <folder>] [-l] [-y YYYY]
        -h          Display help
        -o <folder> Output download to specified folder.
                    Folder is created if it does not exist.
                    Defaults to /tmp
        -l          List downloads available
        -y YYYY     Specify content release year to download that content

Created by: Carl Windus
Init Date: 2016-04-12
Modified on: 2016-04-12 14:00

Licensed under the Creative Commons BY SA license:
    https://creativecommons.org/licenses/by-sa/4.0/

'''

import argparse
import os
import plistlib
import shutil
import urllib
from urlparse import urljoin


class Garageband_Content:
    def __init__(self, base_url=None):
        self.base_url = 'http://audiocontentdownload.apple.com/'
        self.resource_locations = {
            '2016': ['lp10_ms3_content_2016', 'garageband1011.plist'],
            '2015': ['lp10_ms3_content_2015', 'garageband1010.plist'],
        }

    def get_plist(self, year_path, plist_name):
        if not os.path.isdir(self.download_dir):
            os.makedirs(self.download_dir)

        if os.path.isdir(self.download_dir):
            try:
                if not self.list_only:
                    print 'Processing content from: %s' % (self.plist_url)
                    print 'Storing in %s' % self.download_dir
                urllib.urlretrieve(self.plist_url, self.download_plist)
            except:
                raise

    def get_pkgs(self, year_path, plist_name,
                 legacy_dir='lp10_ms3_content_2013'):
        if os.path.exists(self.download_plist):
            gb_plist = plistlib.readPlist(self.download_plist)
            gb_packages = gb_plist['Packages']

            for pkg in gb_packages:
                try:
                    pkg_name = gb_packages[pkg]['DownloadName']
                    if pkg_name.startswith('../%s' % legacy_dir):
                        pkg_name = pkg_name.strip('../')
                        if not os.path.isdir(
                            os.path.join(self.download_dir, legacy_dir)
                        ):
                            os.makedirs(
                                os.path.join(self.download_dir, legacy_dir)
                            )
                        remote_pkg_path = self.base_url + pkg_name
                        local_pkg_path = os.path.join(self.download_dir,
                                                      pkg_name)
                    elif not pkg_name.startswith('../%s' % legacy_dir):
                        remote_pkg_path = self.url_glob + '/' + pkg_name
                        local_pkg_path = os.path.join(self.download_dir,
                                                      pkg_name)

                    if not self.list_only:
                        print 'Downloading %s' % remote_pkg_path
                        urllib.urlretrieve(remote_pkg_path, local_pkg_path)
                    else:
                        print '%s ---> %s' % (remote_pkg_path, local_pkg_path)
                except:
                    raise

    def grab_content(self, year_path, plist_name, output_dir=None,
                     list_only=False):
        if output_dir:
            self.output_dir = output_dir
        else:
            self.output_dir = '/tmp'

        self.url_glob = urljoin(self.base_url, year_path)
        self.plist_url = urljoin(self.url_glob, year_path + '/' + plist_name)
        self.local_plist = os.path.join(year_path, plist_name)
        self.download_dir = os.path.join(self.output_dir, year_path)
        self.download_plist = os.path.join(self.output_dir, self.local_plist)
        if list_only:
            self.list_only = True
        else:
            self.list_only = False

        self.get_plist(year_path, plist_name)
        self.get_pkgs(year_path, plist_name)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-o',
                        type=str,
                        nargs=1,
                        dest='output',
                        metavar='<folder>',
                        help='Download location for GarageBand content',
                        required=False)

    parser.add_argument('-l',
                        action='store_true',
                        dest='list_pkgs',
                        help='List content',
                        required=False)

    parser.add_argument('-y',
                        nargs=1,
                        dest='content_year',
                        metavar='YYYY',
                        help='Download content released in a particular year',
                        required=False)

    args = parser.parse_args()

    if args.output and len(args.output) is 1:
        output = args.output[0]
    elif not args.output:
        output = '/tmp'

    if args.content_year and len(args.content_year) is 1:
        year = args.content_year[0]
    if not args.content_year:
        year = None

    if args.list_pkgs:
        list_only = True
    elif not args.list_pkgs:
        list_only = False

    gc = Garageband_Content()

    if not list_only:
        if not year:
            for year in gc.resource_locations:
                gc.grab_content(gc.resource_locations[year][0],
                                gc.resource_locations[year][1],
                                output)
        elif year:
            gc.grab_content(gc.resource_locations[year][0],
                            gc.resource_locations[year][1],
                            output)
    elif list_only:
        output = '/tmp'
        if not year:
            for year in gc.resource_locations:
                gc.grab_content(gc.resource_locations[year][0],
                                gc.resource_locations[year][1],
                                output, list_only=True)
                try:
                    shutil.rmtree(os.path.join(
                        output, gc.resource_locations[year][0])
                    )
                except:
                    raise
        elif year:
            gc.grab_content(gc.resource_locations[year][0],
                            gc.resource_locations[year][1],
                            output, list_only=True)
            try:
                shutil.rmtree(os.path.join(
                   output, gc.resource_locations[year][0])
                )
            except:
                raise


if __name__ == '__main__':
    main()
