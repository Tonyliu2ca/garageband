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
Modified on: 2016-04-13 08:50
Version: 1.1.0b
Revision notes:
    1.0:    Initial commit
    1.0.1b: Switched to urllib2 with better error handling and implemented
            progress bar, added functions for obtaining the package file
            size, and reporting this in list output.
            Sanitised the list output to only return remote url of package.

Licensed under the Creative Commons BY SA license:
    https://creativecommons.org/licenses/by-sa/4.0/

Progress bar implementation courtesy of Fabio Trevisiol
https://stackoverflow.com/questions/2028517/python-urllib2-progress-hook

'''


import argparse
import os
import plistlib
import shutil
import urllib2
from sys import exit
from sys import stdout


class Garageband_Content:
    def __init__(self, download_location=None):
        self.base_url = 'http://audiocontentdownload.apple.com'
        self.resource_locations = {
            '2016': ['lp10_ms3_content_2016', 'garageband1011.plist'],
            '2015': ['lp10_ms3_content_2015', 'garageband1010.plist'],
        }
        self.legacy_dir = 'lp10_ms3_content_2013'
        if not download_location:
            self.download_location = '/tmp'

    def build_url(self, file_path):
        sep = '/'
        return sep.join(file_path)

    def make_paths(self, folder):
        folder = os.path.join(self.download_location, folder)
        if not os.path.isdir(folder):
            os.makedirs(folder)

    def download_file(self, remote_file, local_file, file_size=None):
        local_file = os.path.join(self.download_location, local_file)

        if file_size:
            human_file_size = self.convert_size(float(file_size))

        try:
            if remote_file.endswith('.pkg'):
                f = open(local_file, 'wb')
                req = urllib2.urlopen(remote_file)
                total_size = int(file_size)
                bytes_so_far = 0
                while True:
                    buffer = req.read(8192)
                    if not buffer:
                        print ''
                        break

                    bytes_so_far += len(buffer)
                    f.write(buffer)
                    percent = float(bytes_so_far) / total_size
                    percent = round(percent*100)
                    stdout.write("\r%s [%0.0f%% of %s]" % (remote_file,
                                                           percent,
                                                           human_file_size))
                    stdout.flush()
            else:
                req = urllib2.urlopen(remote_file)
                with open(local_file, 'wb') as f:
                    f.write(req.read())
                    f.close()

        except (urllib2.URLError, urllib2.HTTPError) as e:
            print '%s' % e
            self.clean_folders()
            exit(1)

    def convert_size(self, file_size, precision=2):
        suffixes = ['B', 'KB', 'MB', 'GB', 'TB']
        suffix_index = 0
        while file_size > 1024 and suffix_index < 4:
            suffix_index += 1
            file_size = file_size/1024.0
        return '%.*f%s' % (precision, file_size, suffixes[suffix_index])

    def build_pkg_list(self, local_plist):
        glob_path = os.path.join(self.download_location, local_plist)
        if os.path.isfile(glob_path):
            gb_pkgs = plistlib.readPlist(glob_path)
            gb_pkgs = gb_pkgs['Packages']
            return gb_pkgs
        else:
            return None

    def check_legacy(self, pkg_name):
        legacy = '../' + self.legacy_dir
        if pkg_name.startswith(legacy):
            return True
        else:
            return False

    def strip_legacy(self, pkg_name):
        return pkg_name.strip('../')

    def clean_folders(self):
        folders = [self.legacy_dir]
        for item in self.resource_locations:
            folders.append(self.resource_locations[item][0])

        for item in folders:
            try:
                shutil.rmtree(os.path.join(
                    self.download_location, item)
                )
            except:
                pass

    def grab_content(self, content_year=None, output_dir=None,
                     list_only=False):
        years = []
        pkg_total_size = []

        if not content_year:
            years = self.resource_locations.keys()
        elif content_year:
            years.append(content_year)

        if output_dir:
            self.download_location = output_dir

        if content_year is '2015':
            self.make_paths(self.legacy_dir)
            self.make_paths(self.resource_locations[content_year][0])

        for year in years:
            self.make_paths(self.resource_locations[year][0])
            self.make_paths(self.legacy_dir)

            local_plist = os.path.join(
                self.resource_locations[year][0],
                self.resource_locations[year][1]
            )

            remote_plist = self.build_url([
                self.base_url,
                self.resource_locations[year][0],
                self.resource_locations[year][1],
            ])

            remote_pkg_stub = self.build_url([
                self.base_url,
                self.resource_locations[year][0]
            ])

            local_pkg_stub = os.path.join(
                self.download_location,
                self.resource_locations[year][0]
            )

            self.download_file(remote_plist, local_plist)

            pkg_list = self.build_pkg_list(local_plist)

            for item in pkg_list:
                pkg = pkg_list[item]['DownloadName']
                pkg_size = pkg_list[item]['DownloadSize']
                pkg_total_size.append(pkg_list[item]['DownloadSize'])

                if self.check_legacy(pkg):
                    pkg = self.strip_legacy(pkg)
                    remote_pkg = self.build_url([self.base_url, pkg])
                    local_pkg = os.path.join(self.download_location,
                                             pkg)
                else:
                    remote_pkg = self.build_url([remote_pkg_stub, pkg])
                    local_pkg = os.path.join(local_pkg_stub, pkg)

                if list_only:
                    print '%s %s' % (
                        remote_pkg,
                        self.convert_size(float(pkg_size))
                    )
                elif not list_only:
                    self.download_file(remote_pkg, local_pkg,
                                       file_size=pkg_size)

        if list_only:
            total_size = sum(pkg_total_size)
            print 'Total size: %s' % self.convert_size(float(total_size))
            self.clean_folders()


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
                        dest='year',
                        metavar='YYYY',
                        choices=['2015', '2016'],
                        help='Content released in a particular year',
                        required=False)

    args = parser.parse_args()

    gc = Garageband_Content()

    if args.output and len(args.output) is 1:
        output = os.path.expandvars(args.output[0])
    elif not args.output:
        output = gc.download_location

    if args.year and len(args.year) is 1:
        year = args.year[0]
    elif not args.year:
        year = None

    if args.list_pkgs:
        list_pkgs = True
    elif not args.list_pkgs:
        list_pkgs = False

    gc.grab_content(content_year=year, list_only=list_pkgs, output_dir=output)

if __name__ == '__main__':
    main()
