#!/usr/bin/python
# -*- coding: utf-8 -*-

### BEGIN LICENSE

# Copyright (C) 2013 National University of Defense Technology(NUDT) & Kylin Ltd

# Author:
#     maclin <majun@ubuntukylin.com>
#     Shine Huang<shenghuang@ubuntukylin.com>  
# Maintainer:
#     maclin <majun@ubuntukylin.com>

# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 3, as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranties of
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR
# PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.

### END LICENSE

import urllib2
import json
import apt

from backend.ubuntu_sw import (SCREENSHOT_THUMB_URL,SCREENSHOT_LARGE_URL)
from models.enums import UBUNTUKYLIN_RES_ICON_PATH

#This class is the abstraction of a 
class Application:

    # work type
    mark = ''
    #
    def __init__(self, pkgname, category_name, apt_cache):
        if not pkgname:
            raise ValueError("Need either appname or pkgname or request")
        self.pkgname = pkgname
        self.category_name = category_name
        if not apt_cache:
            self.package = None
        else:
            try:
                self.package = apt_cache[pkgname]
            except:
                self.package = None
        self.cache = apt_cache
        self.thumbnail_url = None
        self.screenshot_url = None
        self.iconfile = UBUNTUKYLIN_RES_ICON_PATH + pkgname + ".png"
        self.screenshot_list = []
        self.icons = []
        self.reviews = []
        self.rnrStat = None

    @property
    def name(self):
        return self.pkgname

    @property
    def thumbnail(self):
        self.thumbnail_url = SCREENSHOT_THUMB_URL % {
            'pkgname': self.pkgname,
            'version': self.version or 0,
        }

        return self.thumbnail_url

    @property
    def screenshot(self):
        self.screenshot_url = SCREENSHOT_LARGE_URL % {
            'pkgname': self.pkgname,
            'version': self.version or 0,
        }

        return self.screenshot_url

    @property
    def iconfile(self):
        return self.iconfile

    @property
    def description(self):
        return self.package.candidate.description

    @property
    def summary(self):
       return self.package.candidate.summary

    @property
    def packageSize(self):
        return self.package.candidate.size

    @property
    def version(self):
        return self.package.candidate.version

    @property
    def is_installed(self):
        return self.package.is_installed

    @property
    def is_upgradable(self):
        return self.package.is_upgradable

    @property
    def installed_version(self):
        if(self.package.installed is not None):
            return self.package.installed.version
        else:
            return ""

    @property
    def candidate_version(self):
        return self.package.candidate.version


    #get the reviews object list of this application
    def get_reviews(self):
        print "get_reviews_sync"
        return self.reviews


if __name__ == "__main__":

    app = Application("gimp",None)
    print app.name
#    print Application.get_screenshot_list_sync("gimp")


    cache = apt.Cache()
    cache.open()
    print len(cache)
#   print cache
    for item in cache:
        print "\n************************"
        print "fullname:"+item.fullname
#        print "section:" +item.section
        if not item.candidate:
            continue
        print item.candidate.section
        if "Icon" in item.candidate.record:
            print "fullname:"+item.fullname
            print item.candidate.record
#        print item.candidate.uri
     

