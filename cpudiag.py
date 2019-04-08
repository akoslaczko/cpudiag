#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 19 09:48:50 2018

@author: akkus
"""
import time
import datetime
import psutil
import cpuinfo
import curses
import numpy as np
import pandas as pd


# Function to get tables
def create_table(values, history):
    df = pd.DataFrame(values, columns=['Label', 'Current'])
    df.set_index('Label', inplace=True)
    ### Appending to history
    history = np.vstack((history, df['Current']))
    ### Adding stats
    df['Average'] = np.mean(history, axis=0)
    df['Min'] = np.amin(history, axis=0)
    df['Max'] = np.amax(history, axis=0)
    return df, history


# Function to print formatted tables via curses
def print_curses_table(scr, df, cm, sep='\t'):
    ### Header
    scr.addstr(df.index.name + sep, curses.A_BOLD)
    for name in df.columns:
        scr.addstr(name + sep, curses.A_BOLD)
    scr.addstr('\n')
    ### Rows
    for row in df.iterrows():
        scr.addstr(row[0] + sep, curses.A_DIM)
        for cell in row[1]:
            scr.addstr(str(int(cell)) + sep, curses.color_pair(cmap(int(cell), cm)))
        scr.addstr('\n')

     
# Colormapping
cm_load = [25, 50, 75]
cm_clock = [1000, 2500, 4000]
cm_temp = [40, 60, 80]

def cmap(val, cm):
    if val <= cm[0]:
        c = 1
    elif val > cm[0] and val <= cm[1]:
        c = 2
    elif val > cm[1] and val <= cm[2]:
        c = 3
    elif val > cm[2]:
        c = 4
    return c

        
# Main program
def main():
    try:
        # Init curses
        scr = curses.initscr()        
        curses.noecho()
        curses.cbreak()
        curses.halfdelay(10) # Refresh time (tenths of seconds)
        curses.curs_set(0) # To hide cursor
        scr.keypad(1)
        
        # Default screen
        scr_type = 'stats'
        
        # Init colors
        curses.start_color()
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_CYAN, curses.COLOR_BLACK)
        
        # Get cpu info
        info = cpuinfo.get_cpu_info()
        
        # Creating empty history variables
        hist_loads = np.empty((0, psutil.cpu_count()))
        hist_clocks = np.empty((0, psutil.cpu_count()))
        hist_temps = np.empty((0, len(psutil.sensors_temperatures()['coretemp'])))
        
        # Start time
        start = time.time()

        while True:
        
            # Cpu utilization
            loads = [['cpu_%i'%(i+1), load] for i, load in enumerate(psutil.cpu_percent(percpu=True))]
            loads, hist_loads = create_table(loads, hist_loads)
     
            # Cpu freqs
            clocks = [['cpu_%i'%(i+1), freq.current] for i, freq in enumerate(psutil.cpu_freq(percpu=True))]
            clocks, hist_clocks = create_table(clocks, hist_clocks)

            # Cpu temps
            temps = [['core_%i'%(i), temp.current] for i, temp in enumerate(psutil.sensors_temperatures()['coretemp'])]
            temps, hist_temps = create_table(temps, hist_temps)
        
            # Refresh screen
            scr.clear()
            
            if scr_type == 'stats':
                scr.addstr('  ' + info['brand'] + '  \n', curses.A_REVERSE)
                scr.addstr('\n  UPTIME: ' + str(datetime.timedelta(seconds=int(time.time() - start))) + '  \n', curses.A_REVERSE)
                scr.addstr('\n\n  LOAD (%)  \n\n', curses.A_REVERSE)
                print_curses_table(scr, loads, cm_load)
                scr.addstr('\n\n  FREQ (MHz)  \n\n', curses.A_REVERSE)
                print_curses_table(scr, clocks, cm_clock)
                scr.addstr('\n\n  TEMP (C)  \n\n', curses.A_REVERSE)
                print_curses_table(scr, temps, cm_temp)
                
            elif scr_type == 'help':
                scr.addstr('  ' + 'HELP' + '  \n\n', curses.A_REVERSE)
                scr.addstr('h:\tThis help screen\n')
                scr.addstr('s:\tStats screen (default)\n')
                scr.addstr('r:\tReset history and stats\n')
            
            scr.refresh()
        
            # Wait for user or pass after 1 sec         
            key = scr.getch() # Time is set by the halfdelay function
            # Resetting history variables
            if key == ord('r'):
                start = time.time()
                hist_loads = np.empty((0, psutil.cpu_count()))
                hist_clocks = np.empty((0, psutil.cpu_count()))
                hist_temps = np.empty((0, len(psutil.sensors_temperatures()['coretemp'])))
            # Activating chosen screen
            if key == ord('s'):
                scr_type = 'stats'
            if key == ord('h'):
                scr_type = 'help'
        
               
    except KeyboardInterrupt:
        # Clear screen an quit
        curses.echo()
        curses.nocbreak() 
        scr.keypad(0)
        curses.endwin()
        pass


if __name__ == '__main__':
    main()