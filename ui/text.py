###############################################################################
#PPAM is a pulseaudio interface.
#Copyright (C) 2013  Denis Doria (Thuck)
#
#This program is free software; you can redistribute it and/or
#modify it under the terms of the GNU General Public License
#as published by the Free Software Foundation; version 2
#of the License.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program; if not, write to the Free Software
#Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
###############################################################################
import curses
import ui.basic as basic
import ui.tabs as tabs


def main(stdscr):

    #Initial configuration
    curses.curs_set(0)
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    height, width = stdscr.getmaxyx()

    menu = stdscr.subwin(3, width, 0, 0)
    body = stdscr.subwin(height - 6, width, 3, 0)
    footer = stdscr.subwin(3, width, height - 3, 0)

    tab_list = [tabs.TabPlayback(body),
                tabs.TabRecord(body),
                tabs.TabOutputDevices(body),
                tabs.TabInputDevices(body),
                tabs.TabCards(body)]

    top_menu = basic.TopMenu(menu, tab_list)
    footer_menu = basic.FooterMenu(footer)
    top_menu.draw()
    footer_menu.draw()

    top_menu.focus = 1
    tab = top_menu.draw()
    tab.draw()

    stdscr.refresh()
    stdscr.timeout(350)  # Avoid too many refreshes

    while True:
        pressed_key = stdscr.getch()
        if pressed_key == curses.KEY_RESIZE:
            height, width = stdscr.getmaxyx()
            menu = stdscr.subwin(3, width, 0, 0)
            body = stdscr.subwin(height - 6, width, 3, 0)
            footer = stdscr.subwin(3, width, height - 3, 0)

            top_menu.resize_window(menu)
            footer_menu.resize_window(footer)
            for tab in tab_list:
                tab.resize_window(body)

            tab = top_menu.draw()
            footer_menu.draw()
            tab.draw()

        elif pressed_key in (ord('q'),):
            break

        elif pressed_key in (curses.KEY_LEFT, ord('h'),):
            if top_menu.focus - 1 in top_menu.tabs_dict:
                top_menu.focus -= 1
                tab = top_menu.draw()

        elif pressed_key in (curses.KEY_RIGHT, ord('l'),):
            if top_menu.focus + 1 in top_menu.tabs_dict:
                top_menu.focus += 1
                tab = top_menu.draw()

        elif (pressed_key in range(256) and
                chr(pressed_key).isdigit() and
                int(chr(pressed_key)) in top_menu.tabs_dict):
            top_menu.focus = int(chr(pressed_key))
            tab = top_menu.draw()

        else:
            tab.update(pressed_key)

        tab.draw()

        footer_menu.draw()
