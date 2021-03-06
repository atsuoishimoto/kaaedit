import curses, os, sys, types
import setproctitle
import kaa.tools
import kaa.log
from kaa import options, consts, config
from . import app, keydef, frame

from .. import document
#from kaa.filetype.default import defaultmode
from kaa import fileio

CURSES_MOUSEINTERVAL = 200
CURSES_ESCDELAY = '50'

def _init(stdscr):
    curses.start_color()
    curses.use_default_colors()

    curses.raw()
    curses.nonl()
    stdscr.leaveok(1)
#    curses.mousemask(curses.ALL_MOUSE_EVENTS)
#    curses.mouseinterval(CURSES_MOUSEINTERVAL)

def _restore():
    curses.noraw()
    curses.nl()


def run_userinit():
    fname = os.path.join(kaa.app.config.KAADIR, '__kaa__.py')
    if os.path.isfile(fname):
        with open(fname) as f:
            src = f.read()

        code = compile(src, fname, 'exec')
        module = types.ModuleType('__kaa__')
        exec(code, module.__dict__)

        sys.modules['__kaa__'] = module

def main(stdscr):
    conf = config.Config()
    sys.path.insert(0, conf.KAADIR)

    kaa.log.init(conf.LOGDIR)

    _init(stdscr)
    try:
        keydef.init()

        kaa.app = app.CuiApp(conf)
        kaa.app.storage = fileio.FileStorage()

        mainframe = frame.MainFrame(stdscr)
        kaa.app.init(mainframe)

        run_userinit()

        if not opt.file:
            # no file args. show new document.
            doc = fileio.newfile()
            kaa.app.show_doc(doc)
        else:
            for filename in opt.file:
                doc = kaa.app.storage.openfile(filename)
                kaa.app.show_doc(doc)

        kaa.app.run()

        mainframe.destroy()

    finally:
        _restore()

def run():
    setproctitle.setproctitle('kaa')
    parser = options.build_parser()

    global opt
    opt = parser.parse_args()

    if not os.environ.get('ESCDELAY'):
        os.environ['ESCDELAY'] = CURSES_ESCDELAY

    curses.wrapper(main)


if __name__ == '__main__':
    run()
