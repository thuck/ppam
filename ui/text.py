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
import sys
import basic
import tabs
import time
import string

def main(stdscr):

    #Initial configuration
    curses.curs_set(0)
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    height, width = stdscr.getmaxyx()    

    menu = stdscr.subwin(3, width, 0, 0)
    body = stdscr.subwin(height - 6, width, 3, 0)
    footer = stdscr.subwin(3, width, height - 3, 0)
    
#    tab = basic.Welcome(body, footer)
    error = basic.ERROR(body, footer)
    
    #*Each tab is initialize here, and the configuration
    #is passed to them
    #Each tab must handle the configuration, plus body and footer*
    #**If the tab will block (waiting the user input) it must
    #handle the resize error, and also update the footer**

    tab_list = [getattr(tabs, tab_)(body, footer,'a') for tab_ in dir(tabs) if 'Tab' in tab_]
              
    top_menu = basic.TopMenu(menu, tab_list)
    footer_menu = basic.FooterMenu(footer)
    top_menu.draw()
    footer_menu.draw()

    _help = basic.Help(body, footer_menu)    
    
    stdscr.refresh()
    stdscr.timeout(150) #Avoid too many refreshes, but will keep the clock fine
    
    top_menu.focus = 1
    tab = top_menu.draw()

    while True:        
        c = stdscr.getch()
        if c == curses.KEY_RESIZE:
            error.draw("I cannot handle resize...")
            sys.exit(1)
            
        #This is madness, in gnome-terminal the F1 is captured by the window
        #before it arrives to the curses (konsole is ok)
        #gnome-terminal is a crap
        elif c in (curses.KEY_HELP, curses.KEY_F1, ord('H')):
            _help.draw()
            
        elif c in (ord('h'),):
            _help.draw(tab.help)
        
        #TODO: Include a exit cleaner if needed
        #TODO: Include the ctrl+c as a valid exit
        #The event library must be used (it will be a pain)
        elif c in (ord('q'),):
            break
            
        elif c in range(256) and chr(c) in string.printable[:10] and int(chr(c)) in top_menu.tabs_dict:
            top_menu.focus = int(chr(c))
            tab = top_menu.draw()

        else:
            tab.update(c)

        #if tab is not None:
        tab.draw()
            
        footer_menu.draw()
