import unittest

import os


if __name__ == "__main__":

    test_dir = os.path.abspath(os.path.dirname(__file__))
    test_suite = unittest.TestLoader().discover(test_dir, pattern="test_*.py")

    runner = unittest.TextTestRunner(verbosity=3).run(test_suite)
