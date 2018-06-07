# Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/_Framework/Profile.py
# Compiled at: 2018-04-23 20:27:04
from __future__ import absolute_import, print_function, unicode_literals
from functools import wraps, partial
ENABLE_PROFILING = False
if ENABLE_PROFILING:
    import cProfile
    PROFILER = cProfile.Profile()

def profile(fn):
    u"""
    Decorator to mark a function to be profiled. Only mark top level functions
    """
    if ENABLE_PROFILING:

        @wraps(fn)
        def wrapper(self, *a, **k):
            if PROFILER:
                return PROFILER.runcall(partial(fn, self, *a, **k))
            print('Can not profile (%s), it is probably reloaded' % fn.__name__)
            return fn(*a, **k)

        return wrapper
    return fn


def dump(name='default'):
    assert ENABLE_PROFILING
    import pstats
    fname = name + '.profile'
    PROFILER.dump_stats(fname)

    def save_human_data(sort):
        s = pstats.Stats(fname, stream=open('%s.%s.txt' % (fname, sort), 'w'))
        s.sort_stats(sort)
        s.print_stats()

    save_human_data('time')
    save_human_data('cumulative')
