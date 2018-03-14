#!/usr/bin/python

"""
This will notifify the user via Yo that they need to update Chrome if:
* It is installed
* We haven't already told them about this version
"""

import subprocess
import time
import plistlib
import os
import sys
import getpass
import string
from distutils.version import LooseVersion
from Foundation import \
    CFPreferencesSetAppValue, \
    CFPreferencesAppSynchronize, \
    CFPreferencesCopyAppValue, \
    NSDate

BUNDLE_ID = 'com.grahamgilbert.chrome_notifier'

TESTING = False


def run_yo():
    """
    Like, runs Yo
    """
    cmd = [
        '/Library/Management/show_chrome_update_message.sh'
    ]

    subprocess.call(cmd)


def set_pref(pref_name, pref_value):
    """
    Sets a preference
    """
    # pylint: disable=E0602
    CFPreferencesSetAppValue(pref_name, pref_value, BUNDLE_ID)
    CFPreferencesAppSynchronize(BUNDLE_ID)


def pref(pref_name):
    """
    Reads a preference, setting a default if we set any
    """
    default_prefs = {
        # 'last_shown' : NSDate.new(),
    }

    pref_value = CFPreferencesCopyAppValue(pref_name, BUNDLE_ID)
    if pref_value is None:
        pref_value = default_prefs.get(pref_name)
        # we're using a default value. We'll write it out to
        # /Library/Preferences/<BUNDLE_ID>.plist for admin
        # discoverability
        set_pref(pref_name, pref_value)
    if isinstance(pref_value, NSDate):
        # convert NSDate/CFDates to strings
        pref_value = str(pref_value)
    return pref_value


def already_notified(new_version):
    """
    Have we notified on this version before?
    """
    last_version = pref('last_notified')
    if last_version is None:
        # Never notified
        return False
    if LooseVersion(new_version) > LooseVersion(last_version):
        # new version is bigger, hasn't been notified
        return False
    else:
        # New version isn't bigger, we have been notified
        return True


def set_last_version_notified(version):
    """
    This is the last version we notified on
    """
    set_pref('last_notified', version)


def chrome_installed():
    """
    Checks if Google Chrome is installed
    """
    chrome = '/Applications/Google Chrome.app'
    return bool(os.path.exists(chrome))


def get_chrome_version():
    """
    Returns the on disk chrome version
    """
    chrome_info = plistlib.readPlist('/Applications/Google Chrome.app/Contents/Info.plist')
    if 'CFBundleShortVersionString' in chrome_info:
        return chrome_info['CFBundleShortVersionString']
    else:
        return '0'


def running_chrome_version():
    proc = subprocess.Popen(['/bin/ps', '-axo' 'command='],
                            shell=False, stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    (output, dummy_err) = proc.communicate()
    if proc.returncode == 0:
        proc_lines = [item for item in output.splitlines()]
        for line in proc_lines:
            if line.startswith('/Applications/Google Chrome.app/Contents/Versions/'):
                line = line.replace('/Applications/Google Chrome.app/Contents/Versions/', '')
                if line:
                    sep = '/'
                    line = line.split(sep, 1)[0]
                    return line


def main():
    """
    gimmie some main
    """

    running = False

    running_version = running_chrome_version()
    if not running_version:
        print 'Chrome is not running'
        time.sleep(30)
        sys.exit(0)

    if TESTING is True:
        running = True

    if TESTING is True:
        sleep_seconds = 0
    else:
        sleep_seconds = 20

    if not chrome_installed():
        print 'Chrome not installed'
        time.sleep(30)
        sys.exit(0)

    current_chrome_version = get_chrome_version()

    if current_chrome_version == '0':
        print 'Could not get current chrome version'
        time.sleep(30)
        sys.exit(0)

    if LooseVersion(running_version) < LooseVersion(current_chrome_version):
        print "running version is {}".format(running_version)
        print "on disk version is {}".format(current_chrome_version)
        running = True

    if already_notified(get_chrome_version()):
        print 'Already notified for this version'
        time.sleep(30)
        sys.exit(0)

    if running is True or TESTING is True:
        print 'We are running...'
        time.sleep(sleep_seconds)
        set_last_version_notified(get_chrome_version())


if __name__ == '__main__':
    main()
