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
import time
import curses
import sys

def draw_info_window(win, info_data):
        #This will create a centralize window
        height, width = win.getmaxyx()
        box = win.derwin(height/2, width/2, height/4, width/4)
        hb_height, hb_width = box.getmaxyx()
        box.hline(hb_height - 3, 1, curses.ACS_HLINE, hb_width - 2)
        message = "Press i or p to continue"
        box.addstr(hb_height - 2, hb_width/2 - len(message)/2, message )
        box.box()

        for line_number, info in enumerate(info_data):
            if len(info) >= hb_width - 1:
                info = info[:hb_width - 5] + '...'

            if line_number < hb_height - 4:
                box.addstr(line_number + 1, 1, info)

            else:
                break

        box.refresh()

class Welcome(object):
    """This class handle the Welcome Message"""
    
    def __init__(self, win, footer):
        self.win = win
        self.height, self.width = self.win.getmaxyx()
        self.help = ["I'm the Welcome tab.", 
                     "You don't need help for me."]
        
    def draw(self):
        self.win.erase()
        self.win.box()
        message = 'Welcome'
        self.win.addstr(self.height/2, self.width/2 - len(message)/2, message)
        self.win.refresh()    
        
class Help(object):
    """This class handle the Help"""
    
    def __init__(self, win, footer):
        self.win = win
        self.height, self.width = self.win.getmaxyx()
        self.footer = footer
        
    def draw(self, tab = None):        
        self.win.box()
        #This will create a centralize window
        help_box = self.win.derwin(self.height/2, self.width/2, self.height/4, self.width/4)
        hb_height, hb_width = help_box.getmaxyx()
        help_box.erase()
        help_box.hline(hb_height - 3, 1, curses.ACS_HLINE, hb_width - 2)
        message = "Press any key to continue"
        help_box.addstr(hb_height - 2, hb_width/2 - len(message)/2, message )
        help_box.box()
        if not tab:
            help_box.addstr(1, 1, "Global Help")
        else:
            count = 0
            for i in tab:
                help_box.addstr(count + 1, 1, i)
                count += 1
        self.win.refresh()
        
        help_box.timeout(500)
        while True:
            
            c = help_box.getch()
            
            if c == curses.KEY_RESIZE:
                error = ERROR(self.win, self.footer)
                error.draw("I cannot handle resize...")
                
                sys.exit(1)
            elif  c != -1:
                break
                
            self.footer.draw()
        
class ERROR(object):
    """This class handle the errors, since its difficult to control it"""
    
    def __init__(self, win, footer):
        self.win = win
        self.height, self.width = self.win.getmaxyx()
        
    def draw(self, message):
        self.win.erase()
        self.win.box()
        self.win.addstr(1, 1, message)
        
        for i in range(5, 0, -1):
            self.win.addstr(2, 1, "Exiting in %d" % (i))
            self.win.refresh()
            time.sleep(1)

class TopMenu(object):
    """This class handle the top menu, also it used to store the tabs and control the focus"""
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
        _help = 'Per Tab help press h. Global help press H.'
        if len(_help) > self.height:
            self.win.addstr(1, self.width/2 - len(_help)/2, _help, curses.color_pair(1))
        self.win.refresh()
        
