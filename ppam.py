import curses
import sys
import ui.text

if __name__ == '__main__':
    try:
        curses.wrapper(ui.text.main)

    except KeyboardInterrupt:
        sys.exit(0)

    except curses.error as e:
        print('Not enough screen space: %s' % (e))
        sys.exit(1)
    

