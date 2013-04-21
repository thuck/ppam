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


def draw_info_window(win, info_data):
    #The cake is a lie
    height, width = win.getmaxyx()
    box = win.derwin(height - 2, width//2 - 1, 1, width//2)
    hb_height, hb_width = box.getmaxyx()
    box.erase()
    box.hline(hb_height - 3, 1, curses.ACS_HLINE, hb_width - 2)
    message = "Press c to continue"
    box.addstr(hb_height - 2, hb_width//2 - len(message)//2, message)
    box.border(' ', ' ', ' ', ' ')
    for line_number, info in enumerate(info_data):
        if len(info) >= hb_width - 1:
            info = info[:hb_width - 5] + '...'

        if line_number < hb_height - 4:
            box.addstr(line_number + 1, 1, info)

        else:
            break

    box.refresh()


class TopMenu(object):
    """This class handle the top menu, also it used to store
       the tabs and control the focus"""
    def __init__(self, win, tabs):
        self.win = win
        self.tabs_menu = tuple(enumerate(tabs, 1))
        self.tabs_dict = dict(enumerate(tabs, 1))
        self.height, self.width = self.win.getmaxyx()
        self.focus = -1

    def resize_window(self, win):
        self.win = win
        self.height, self.width = self.win.getmaxyx()

    def draw(self):
        """Draw the top menu, and control the tab focus"""

        self.win.erase()
        self.win.box()
        tab_focused = None
        x = 1

        #Here we highlight (focus) the tab
        for index, tab in self.tabs_menu:
            menu_item = str(index) + '.' + tab.name
            if self.focus == index:
                self.win.addstr(1, x, menu_item, curses.color_pair(1))
                tab_focused = tab

            else:
                self.win.addstr(1, x, menu_item)

            x += len(menu_item) + 2

        self.win.refresh()

        return tab_focused


class FooterMenu(object):
    def __init__(self, win):
        self.win = win
        self.height, self.width = self.win.getmaxyx()

    def resize_window(self, win):
        self.win = win
        self.height, self.width = self.win.getmaxyx()

    def draw(self):
        self.win.erase()
        self.win.box()
        _help = 'Per Tab help press H.'
        if len(_help) > self.height:
            self.win.addstr(1, self.width//2 - len(_help)//2,
                            _help, curses.color_pair(1))
        self.win.refresh()
