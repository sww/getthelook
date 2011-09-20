import imp
import os
import re
import sys
import urlparse

from datetime import datetime
from optparse import OptionParser

from selenium import webdriver

class Photog(object):

    def __init__(self):
        self.drivers = {
            'firefox': webdriver.Firefox,
            'chrome': webdriver.Chrome
        }

        self.active_drivers = []

    def look(self, drivers, urls, options):
        for driver in drivers:
            if driver in self.drivers:
                try:
                    browser = self.drivers.get(driver)()
                    self.active_drivers.append(browser)
                except Exception, msg:
                    sys.stderr.write('%s: %s' % (Exception, msg))
                    continue
            else:
                sys.stderr.write('No driver for %s.' % driver)
                continue

            for url in urls:
                url = url.strip()
                site_name = urlparse.urlparse(url).netloc

                if not options.green:
                    if not os.path.exists(os.path.join(options.screenshot_dir, site_name)):
                        os.mkdir(os.path.join(options.screenshot_dir, site_name))

                browser.get(url)
                # Check for further instructions.
                try:
                    try:
                        mod = imp.find_module(site_name.replace('.', '_'), [options.extension_dir])
                    except ImportError:
                        mod = imp.find_module(site_name.lstrip('www.').replace('.', '_'), [options.extension_dir])

                    blueprint = imp.load_module('blueprint', *mod)
                    blueprint.check_site(url, browser)
                except ImportError, msg:
                    #print sys.stderr.write('%s: %s\n' % (ImportError, msg))
                    pass
                except AttributeError, msg:
                    sys.stderr.write('%s\n' % msg)
                    continue

                if not options.green:
                    filename = '-'.join([datetime.strftime(datetime.now(), '%Y%m%d_%H%M%S'), self.clean_filename(url), driver])
                    filename = os.path.join(options.screenshot_dir, site_name, filename + '.png')
                    print 'saving %s' % filename
                    browser.get_screenshot_as_file(filename)

                if options.interactive:
                    self.prompt()

            browser.close()
            self.active_drivers.remove(browser)

    def clean_filename(self, filename):
        filename = re.sub('^http(|s)://', '', filename)
        return re.sub('[/-\?]', '.', filename)

    def prompt(self):
        while True:
            print 'Continue? [Y/n] ',
            cont = raw_input()
            if cont.lower() == 'n':
                continue
            else:
                return

    def __del__(self):
        for driver in self.active_drivers:
            driver.close()

def main(browsers, urls, options):
    look = Photog()

    if isinstance(urls, str):
        urls = [urls]

    if getattr(options, 'file'):
        try:
            with open(options.file) as f:
                # So we can get from both the cmd line arguments and the file.
                urls += f.readlines()
        except IOError:
            sys.stderr.write('Bad source file')
            return

    if not urls:
        sys.stderr.write('No URLs.')
        return

    look.look(browsers, urls, options)

if __name__ == '__main__':
    browsers = []
    def callback(option, opt_str, value, parser):
        browsers.append(opt_str.strip('--'))
        return

    parser = OptionParser()
    parser.add_option('--chrome', action='callback', callback=callback)
    parser.add_option('--firefox', action='callback', callback=callback)
    parser.add_option('-g', '--green', action='store_true', default=False, help='Do not take screenshots')
    parser.add_option('-i', '--interactive', action='store_true', default=False, help='Control when you go to the next site')
    parser.add_option('-d', '--extension_dir', dest='extension_dir', default='extensions', help='Look for directions in this DIRECTORY', metavar='DIRECTORY')
    parser.add_option('-s', '--screenshot_dir', dest='screenshot_dir', default='screenshots', help='Save screenshots to DIRECTORY', metavar='DIRECTORY')
    parser.add_option('--file', help='Read URLs from FILE', metavar='FILE')

    # args = urls, or a file
    (options, args) = parser.parse_args()

    if not args and not options.file:
        sys.stderr.write('Need URLs.\n')
        sys.exit(2)

    if not browsers:
        sys.stderr.write('No browsers to test.\n')
        sys.exit(2)

    main(browsers, args, options)
