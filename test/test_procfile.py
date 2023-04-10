from inspect import getfile, currentframe
from pathlib import Path
from unittest import TestCase
import os
import sys

PACKAGE_PATH = os.path.join(Path(getfile(currentframe())).resolve().parents[1])
if PACKAGE_PATH not in sys.path:
    sys.path.insert(0, PACKAGE_PATH)


class TestProcfile(TestCase):

    def setUp(self):
        self.proc_file = os.path.join(PACKAGE_PATH, "Procfile")

    def testProcfile(self):
        self.assertTrue(os.path.isfile(self.proc_file))
        with open(self.proc_file, "r") as f:
            self.assertEqual("web: gunicorn --bind 0.0.0.0:8080 --pythonpath app wsgi:app", f.read())
