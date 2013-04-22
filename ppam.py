import curses
import sys
import ui.text
import gettext
from gettext import gettext as _

if __name__ == '__main__':
    gettext.install('ppam')
    try:
        curses.wrapper(ui.text.main)

    except KeyboardInterrupt:
        sys.exit(0)

    except curses.error as err:
        message = _('Not enough screen space')
        print('%s: %s' % (message, err))
        sys.exit(1)
    

