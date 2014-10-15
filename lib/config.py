__author__ = 'qipanguan'
# !/bin/env python2.6
# -*- coding: utf-8 -*-
# Load config from default config director
import ConfigParser


class Config(object):
    def __init__(self, dest=""):
        self.config_parser = ConfigParser.ConfigParser()

        if not dest:
            self.config_parser.read('../etc/checker.etc')
        else:
            try:
                self.config_parser.read(dest)
            except Exception, e:
                print e
