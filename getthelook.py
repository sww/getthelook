import os
import re

from datetime import datetime
from optparse import OptionParser

from selenium import webdriver

class Look(object):

    def __init__(self):
        self.drivers = {
            'firefox': webdriver.Firefox,
            'chrome': webdriver.Chrome
        }

    def look(self, drivers, urls, options):
        if not urls:
            print 'No URLs.'
            return
        if not drivers:
            print 'No drivers.'
            return

        dir_name = datetime.strftime(datetime.now(), '%Y%m%d_%H%M%S')
        os.mkdir(dir_name)

        for driver in drivers:
            if driver in self.drivers:
                try:
                    browser = self.drivers.get(driver)()
                except Exception, msg:
                    print Exception, msg
                    continue
            else:
                print 'No driver for %s' % driver
                continue

            for url in urls:
                browser.get(url)
                filename = '-'.join([self.clean_filename(url), driver])
                filename = os.path.join(dir_name, filename + '.png')
                print 'saving %s' % filename
                browser.get_screenshot_as_file(filename)
            browser.close()

    def clean_filename(self, filename):
        return re.sub('[/-\?]', '.', filename)

def main(browsers, args, options):
    look = Look()
    look.look(browsers, args, options)

if __name__ == '__main__':
    browsers = []
    def callback(option, opt_str, value, parser):
        browsers.append(opt_str.strip('--'))
        return

    parser = OptionParser()
    parser.add_option('--chrome', action='callback', callback=callback)
    parser.add_option('--firefox', action='callback', callback=callback)
    (options, args) = parser.parse_args()

    # if not args:
    #     return

    main(browsers, args, options)
