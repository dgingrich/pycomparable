from setuptools import setup, find_packages, Command


class readme(Command):
    """Subclass build_py to build the README"""
    user_options = []
    initialize_options = finalize_options = lambda self: None
    def run(self):
        from pycomparable import __doc__
        file('README', 'w').write(__doc__)      # Destructive!


setup(
    name = "pycomparable",
    version = "0.1",
    description = "Rich comparison auto-generator decorator",
    license = "BSD",
    packages = find_packages(),
    author = "David Gingrich",
    author_email = "dave@ndanger.org",
    # Internals
    test_suite = 'nose.collector',
    cmdclass = {'readme':readme}
    )
