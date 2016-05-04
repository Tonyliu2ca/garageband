#!/usr/bin/python
'''Downloads Apple Audio content that is installed on first run for
applications such as GarageBand or Logic Pro.

Usage:
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

Examples:
    ./get_audio_content.py -l -p logicpro -y 2015
        Lists all Logic Pro X content released in 2015.

    ./get_audio_content.py -y 2013 2015
        Downloads all GarageBand content for 2013, and 2015.

Created by: Carl Windus
Init Date: 2016-04-12
Modified on: 2016-04-14 22:36
Version: 1.0.4b
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
    1.0.4b  Added support for Logic Pro X audio content. Ignores duplicate
            package paths based on URL, as GarageBand and Logic Pro X share
            similar packages for content.
            Added the -p flag to choose between either 'garageband' or
            'logicpro' content. If the -p flag is not supplied, defaults to
            GarageBand, as the Logic Pro X content is crazy big.
            Added -v flag for verbose output. Default is to be quiet, this
            means list output will not check remote file size unless the -v
            flag is passed.
    1.0.5b  Added simple proxy code for testing. Mutually exclusive options
            for -o and -l. Clean up temp contents when KeyboardInterrupt is
            triggered during list operation.

Licensed under the Creative Commons BY SA license:
    https://creativecommons.org/licenses/by-sa/4.0/

Progress bar implementation courtesy of Fabio Trevisiol
https://stackoverflow.com/questions/2028517/python-urllib2-progress-hook

*** Disclaimer ***
The intent of this tool is to allow a licensed user to trivially download
audio content related to properly licensed versions of Apple software and
the related content downloaded on first run, or after in app purchases are
made.

'''


import argparse
import os
import plistlib
import shutil
import subprocess
import urllib2
from sys import argv
from sys import exit
from sys import stdout
from time import sleep


class Audio_Content:
    version = '1.0.5b'
    name = argv[0]

    def __init__(self, download_location=None):
        self.proxy = urllib2.ProxyHandler()
        self.proxy_opener = urllib2.build_opener(self.proxy)
        self.base_url = 'http://audiocontentdownload.apple.com'
        self.cy_stub = 'lp10_ms3_content_'
        self.resource_locations = {
            '2016': [
                'garageband1011.plist',
                'logicpro1022.plist',
                ],
            '2015': [
                'garageband1010.plist',
                'logicpro1010.plist',
                'logicpro1020.plist',
                ],
            '2013': [
                'garageband1000_en.plist',
                'logicpro1000_en.plist',
                ],
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
        self.pkg_set = ['garageband', 'logicpro']
        self.legacy_dir = 'lp10_ms3_content_2013'
        if not download_location:
            self.download_location = ('/tmp')

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
                remote_file.endswith('.pkg') or remote_file.endswith('.mpkg')
            ):
                with open(local_file, 'wb') as f:
                    # f = open(local_file, 'wb')
                    req = self.proxy_opener.open(remote_file)
                    # req = urllib2.urlopen(remote_file)
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
                # req = urllib2.urlopen(remote_file)
                req = self.proxy_opener.open(remote_file)
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

    def convert_plist(self, local_file):
        subprocess.check_call(['/usr/bin/plutil',
                               '-convert',
                               'xml1',
                               local_file],
                              stdout=None,
                              stderr=None)

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
            self.convert_plist(glob_path)
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
            try:
                path = os.path.join(self.download_location)
                shutil.rmtree(path)
            except:
                pass

    def grab_content(self, content_year=None, output_dir=None,
                     list_only=False, package_set=None, verbosity=False):
        years = []
        pkg_total_size = []
        plists_to_get = []
        build_dirs = []
        pkg_list = []
        if not content_year:
            years = self.resource_locations.keys()
        elif content_year:
            for year in content_year:
                years.append(year)
        years.sort()
        for cy in self.resource_locations:
            if cy in years:
                for item in self.resource_locations[cy]:
                    if package_set in item:
                        cy_path = self.cy_stub + cy
                        if cy_path not in build_dirs:
                            build_dirs.append(cy_path)
                        cy_path = self.build_url([self.base_url,
                                                  cy_path,
                                                  item])
                        if cy_path not in plists_to_get:
                            plists_to_get.append(cy_path)

        if output_dir:
            self.download_location = os.path.join(output_dir, package_set)
            if verbosity:
                print '%s - version: %s' % (self.name, self.version)
                print 'Content downloads to:\n\t%s' % self.download_location
                print 'Downloading remote plist:'
                for rp in plists_to_get:
                    print '\t%s' % rp
        for year in years:
            for bd in build_dirs:
                path = os.path.join(self.download_location, bd)
                self.make_paths(path)
            for rp in plists_to_get:
                lp = os.path.join(self.download_location,
                                  '/'.join(rp.split('/')[3:]))
                cy = rp.split('/')[3]
                self.download_file(rp, lp)
                pkgs = self.build_pkg_list(lp, cy)
                for pkg in pkgs:
                    if pkg not in pkg_list:
                        pkg_list.append(pkg)
        pkg_list.sort()
        if verbosity:
            print 'Storing files in:'
            for bd in build_dirs:
                print '\t%s' % os.path.join(self.download_location, bd)
        for pkg in pkg_list:
            dl_url = self.build_url([self.base_url, pkg])
            pkg_save_path = os.path.join(self.download_location, pkg)
            if list_only:
                if verbosity:
                    size = self.list_size(dl_url)
                    pkg_total_size.append(size)
                    size = self.convert_size(float(size))
                    print '%s [%s]' % (dl_url, size)
                if not verbosity:
                    print '%s' % dl_url
            elif not list_only:
                if not self.file_test(dl_url, pkg_save_path):
                    self.download_file(dl_url, pkg_save_path)
                else:
                    print 'Already downloaded %s' % dl_url
        if list_only:
            if verbosity:
                hs = []
                for item in pkg_total_size:
                    hs.append(int(item))
                ts = self.convert_size(sum(hs))
                print 'Total: %s' % ts
            self.clean_up()


def main():
    class SaneUsageFormat(argparse.HelpFormatter):
        """
            for matt wilkie on SO
            http://stackoverflow.com/questions/9642692/argparse-help-without-duplicate-allcaps/9643162#9643162
        """
        def _format_action_invocation(self, action):
            if not action.option_strings:
                default = self._get_default_metavar_for_positional(action)
                metavar, = self._metavar_formatter(action, default)(1)
                return metavar

            else:
                parts = []

                # if the Optional doesn't take a value, format is:
                #    -s, --long
                if action.nargs == 0:
                    parts.extend(action.option_strings)

                # if the Optional takes a value, format is:
                #    -s ARGS, --long ARGS
                else:
                    default = self._get_default_metavar_for_optional(action)
                    args_string = self._format_args(action, default)
                    for option_string in action.option_strings:
                        parts.append(option_string)

                    return '%s %s' % (', '.join(parts), args_string)

                return ', '.join(parts)

        def _get_default_metavar_for_optional(self, action):
            return action.dest.upper()

    parser = argparse.ArgumentParser(formatter_class=SaneUsageFormat)

    ac = Audio_Content()
    group = parser.add_mutually_exclusive_group()
    parser.add_argument('-p', '--pkgs',
                        type=str,
                        nargs=1,
                        dest='dl_pkg_set',
                        metavar='<pkg set>',
                        choices=ac.pkg_set,
                        help='app to download content for - %s.' % ac.pkg_set,
                        required=False)
    group.add_argument('-o', '--output',
                       type=str,
                       nargs=1,
                       dest='out',
                       metavar='<folder>',
                       help='download location.',
                       required=False)
    group.add_argument('-l', '--list',
                       action='store_true',
                       dest='list_pkgs',
                       help='list content',
                       required=False)
    parser.add_argument('-v', '--verbose',
                        action='store_true',
                        dest='verbose',
                        help='verbose output',
                        required=False)

    parser.add_argument('-y', '--year',
                        nargs='*',
                        dest='year',
                        metavar='YYYY',
                        choices=ac.year_choices,
                        help='content released in year',
                        required=False)
    args = parser.parse_args()
    if args.dl_pkg_set:
        get_pkg_set = args.dl_pkg_set[0]
    elif not args.dl_pkg_set:
        get_pkg_set = ac.pkg_set[0]

    if args.out and len(args.out) is 1:
        output = os.path.expandvars(args.out[0])
    elif not args.out:
        output = ac.download_location

    if args.year:
        year = args.year
    elif not args.year:
        year = None

    if args.list_pkgs:
        list_pkgs = True
    elif not args.list_pkgs:
        list_pkgs = False

    if args.verbose:
        verbose = True
    else:
        verbose = False

    try:
        ac.grab_content(content_year=year,
                        list_only=list_pkgs,
                        output_dir=output,
                        package_set=get_pkg_set,
                        verbosity=verbose)
    except KeyboardInterrupt:
            print ''
            if list_pkgs:
                ac.clean_up()
            exit(1)


if __name__ == '__main__':
    main()
