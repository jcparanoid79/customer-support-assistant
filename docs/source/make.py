#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

sys.path.insert(0, os.path.abspath('../..'))

from sphinx.cmd.build import main

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
