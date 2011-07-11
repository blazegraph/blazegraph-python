import os

try:
    from Cython.Distutils import build_ext as build_pyx
    import Cython.Compiler.Version
    CYTHON_INSTALLED = True
except ImportError:
    CYTHON_INSTALLED = False

try:
    from setuptools.extension import _Extension as RealExtension
    from distutils.extension import Extension as StupidExtension
    class Extension(StupidExtension):
        def __init__(self, *args, **kwargs):
            RealExtension.__init__(self, *args, **kwargs)
except ImportError:
    from distutils.extension import Extension

PACKAGE_PATH='./pymantic/'

def ext_modules():
    if CYTHON_INSTALLED:
        source_extension = ".pyx"
        print("Building with Cython %s." % Cython.Compiler.Version.version)

        from Cython.Compiler import Options
        Options.generate_cleanup_code = 3
    else:
        source_extension = ".c"
        if not os.path.exists(PACKAGE_PATH + 'pymantic.raptor.raptor_c.c'):
            print ("WARNING: Trying to build without Cython, but pre-generated "
                   "'%spymantic.raptor.raptor_c.c' does not seem to be available." % PACKAGE_PATH)
        else:
            print ("Building without Cython.")

    result = []
    try:
        result.append(
            Extension(
            'pymantic.raptor.raptor_c',
            sources = [PACKAGE_PATH + 'pymantic.raptor.raptor_c' + source_extension],
            libraries = ['raptor2'],
            ))
    return result

def extra_setup_args():
    result = {}
    if CYTHON_INSTALLED:
        result['cmdclass'] = {'build_ext': build_pyx}
    return result
