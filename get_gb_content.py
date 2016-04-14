#!/usr/bin/python
'''Downloads the free GarageBand content that is installed on first run.
Usage:
    ./get_gb_content.py [-h] [-o <folder>] [-l] [-y YYYY]
        -h          Display help
        -o <folder> Output download to specified folder.
                    Folder is created if it does not exist.
                    If -o is not supplied, default location is /tmp
        -l          List downloads available
        -y YYYY     Specify content release year to download that content

Created by: Carl Windus
Init Date: 2016-04-12
Modified on: 2016-04-14 22:36
Version: 1.0.3b
Revision notes:
    1.0:    Initial commit
    1.0.1b: Switched to urllib2 with better error handling and implemented
            progress bar, added functions for obtaining the package file
            size, and reporting this in list output.
            Sanitised the list output to only return remote url of package.
    1.0.2b: Fixed the rounding errors, and switched to getting the file size
            remotely rather than from the plist.
    1.0.3b: Found a number of additional loops that aren't listed in the 2015
            GarageBand plist file, so added those in. Also found the 2013
            plist file, so switch to using that. This may result in a couple
            of extraneous packages downloaded.
            Also added a test to check if the file is already downloaded and
            if so, skip the download.
            When killing the script via KeyboardInterrupt, the script now
            cleans up folders, and exits somewhat more gracefully.
            Note - this clean up will remove any and all completed downloads!

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
from time import sleep


class Garageband_Content:
    def __init__(self, download_location=None):
        self.base_url = 'http://audiocontentdownload.apple.com'
        self.resource_locations = {
            '2016': ['lp10_ms3_content_2016', 'garageband1011.plist'],
            '2015': ['lp10_ms3_content_2015', 'garageband1010.plist'],
            '2013': ['lp10_ms3_content_2013', 'garageband1000_en.plist'],
        }
        self.premium_loops = {
            '2015': [
                'MAContent10_PremiumPreLoopsHipHop.pkg',
                'MAContent10_PremiumPreLoopsElectroHouse.pkg',
                'MAContent10_PremiumPreLoopsDubstep.pkg',
                'MAContent10_PremiumPreLoopsModernRnB.pkg',
                'MAContent10_PremiumPreLoopsTechHouse.pkg',
                'MAContent10_PremiumPreLoopsDeepHouse.pkg',
                'MAContent10_PremiumPreLoopsChillwave.pkg',
                'MAContent10_PremiumPreLoopsGarageBand.pkg',
                'MAContent10_PremiumPreLoopsJamPack1.pkg',
                'MAContent10_PremiumPreLoopsRemixTools.pkg',
                'MAContent10_PremiumPreLoopsRhythmSection.pkg',
                'MAContent10_PremiumPreLoopsSymphony.pkg',
                'MAContent10_PremiumPreLoopsWorld.pkg',
            ]
        }
        self.year_choices = self.resource_locations.keys()
        self.year_choices.sort()
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

    def download_file(self, remote_file, local_file):
        try:
            if (
                remote_file.endswith('.pkg')
                or remote_file.endswith('.mpkg')
            ):
                f = open(local_file, 'wb')
                req = urllib2.urlopen(remote_file)
                try:
                    ts = req.info().getheader('Content-Length').strip()
                    human_fs = self.convert_size(float(ts))
                    header = True
                except AttributeError:
                    try:
                        ts = req.info().getheader('Content-Length').strip()
                        human_fs = self.convert_size(float(ts))
                        header = True
                    except AttributeError:
                        header = False
                        human_fs = 0
                if header:
                    ts = int(ts)
                bytes_so_far = 0
                while True:
                    buffer = req.read(8192)
                    if not buffer:
                        print ''
                        break

                    bytes_so_far += len(buffer)
                    f.write(buffer)
                    if not header:
                        ts = bytes_so_far

                    percent = float(bytes_so_far) / ts
                    percent = round(percent*100, 2)
                    stdout.write("\r%s [%0.2f%% of %s]" % (remote_file,
                                                           percent,
                                                           human_fs))
                    stdout.flush()
            else:
                req = urllib2.urlopen(remote_file)
                with open(local_file, 'wb') as f:
                    f.write(req.read())
                    f.close()
        except (urllib2.URLError, urllib2.HTTPError) as e:
            print '%s' % e
            self.clean_up()
            exit(1)
        sleep(0.05)

    def list_size(self, remote_file):
        try:
            req = urllib2.urlopen(remote_file)
            ts = req.info().getheader('Content-Length').strip()
            req.close()
            return ts
        except AttributeError:
            return 0

    def file_test(self, remote_file, local_file):
        if os.path.exists(local_file):
            remote_size = self.list_size(remote_file)
            remote_size = round(float(remote_size), 2)
            local_size = os.path.getsize(local_file)
            local_size = round(float(local_size), 2)
            if local_size == remote_size:
                return True
            else:
                return False
        else:
            return False

    def convert_size(self, file_size, precision=2):
        suffixes = ['B', 'KB', 'MB', 'GB', 'TB']
        suffix_index = 0
        while file_size > 1024 and suffix_index < 4:
            suffix_index += 1
            file_size = file_size/1024.0
        return '%.*f%s' % (precision, file_size, suffixes[suffix_index])

    def build_pkg_list(self, local_plist, content_year):
        glob_path = os.path.join(self.download_location, local_plist)
        if os.path.isfile(glob_path):
            gb_pkgs = plistlib.readPlist(glob_path)
            gb_pkgs = gb_pkgs['Packages']
            gb_pkgs_list = []
            for item in gb_pkgs:
                pkg = gb_pkgs[item]['DownloadName']
                if self.check_legacy(pkg):
                    pass
                else:
                    pkg = os.path.join(content_year, pkg)
                    gb_pkgs_list.append(pkg)
            if '2015' in content_year:
                for item in self.premium_loops['2015']:
                    pkg = os.path.join(content_year, item)
                    gb_pkgs_list.append(pkg)
            return gb_pkgs_list
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

    def clean_up(self, filename=None):
        if filename:
            try:
                os.remove(filename)
            except:
                pass
        elif not filename:
            folders = []
            for item in self.resource_locations:
                folders.append(self.resource_locations[item][0])
            for item in folders:
                try:
                    path = os.path.join(self.download_location,
                                        item)
                    shutil.rmtree(path)
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
        years.sort()
        if output_dir:
            self.download_location = output_dir
        for year in years:
            cy_path = self.resource_locations[year][0]
            cy_plist = self.resource_locations[year][1]
            local_cy_path = os.path.join(self.download_location, cy_path)
            local_plist = os.path.join(local_cy_path, cy_plist)
            remote_plist = self.build_url([self.base_url, cy_path, cy_plist])
            self.make_paths(local_cy_path)
            self.download_file(remote_plist, local_plist)
            pkg_list = self.build_pkg_list(local_plist, cy_path)
            for pkg in pkg_list:
                dl_url = self.build_url([self.base_url, pkg])
                pkg_save_path = os.path.join(self.download_location, pkg)
                if list_only:
                    size = self.list_size(dl_url)
                    pkg_total_size.append(size)
                    size = self.convert_size(float(size))
                    print '%s [%s]' % (dl_url, size)
                elif not list_only:
                    if not self.file_test(dl_url, pkg_save_path):
                        self.download_file(dl_url, pkg_save_path)
                    else:
                        print 'Already downloaded %s' % dl_url
            self.clean_up(local_plist)
        if list_only:
            hs = []
            for item in pkg_total_size:
                hs.append(int(item))
            ts = self.convert_size(sum(hs))
            print 'Total: %s' % ts
            self.clean_up()


def main():
    gc = Garageband_Content()
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
                        choices=gc.year_choices,
                        help='Content released in a particular year',
                        required=False)
    args = parser.parse_args()
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

    try:
        gc.grab_content(content_year=year,
                        list_only=list_pkgs,
                        output_dir=output)
    except KeyboardInterrupt:
            print ''
            gc.clean_up()
            exit(1)


if __name__ == '__main__':
    main()
