'''
Class gcode written by Ryan Zambrotta
'''

# imports -----------------------------------------------------------------------
from pyvector import * # this imports numpy as np
from gcode_line import gcode_line
from gcode_settings import gcode_settings
from helper import *
from visual import *


# Contains names of all the method in gcode object and their translation actual
METHODS = {'G0':'rapid move','G1':'move','G20':'use in','G21':'use mm','F':'set speed',
              'G90':'abs coords','G91':'rel coords','E':'extrude','G28':'go home',
              'M790':'new layer',';':'comment'}




# Main GCODE class -------------------------------------------------------------

class gcode():

    def __init__(self, debug_mode=False, settings=None, preallocate=500):
        '''
        Parameters:

        > DEBUG_MOVE:
        > SETTINGS:
        > PREALLOCATE:
        '''

        # settings
        if not settings:
            # uses default settings
            self.settings = gcode_settings()
            
        elif type(settings) != gecode_settings:
            # type of settings is incorrect
            raise TypeError('Settigns object must be of type gecode_settings')
        else:
            # settings is good to go!
            self.settings = settings

        # creating memory blocks for GCODE
        self.code = []

        # number of lines written
        self.count = 0

        # creating motion history with preallocated vector
        self.history = vec2d(shape=(int(preallocate),3))

        # records the current and previous position
        self.current_pos = np.zeros(3)
        self.previous_pos = np.zeros(3)

        # determines whether to only print lines of gcode to screen or to only save to memory
        self.debug = debug_mode

        # sets the default motion type for move (absolute coordinates)
        self.coords = 'abs'

        # sets default for
        self.unit_sys = 'mm'

        # creating a library for user defined commands
        self.user_lib = {}

        # internal recording of the total print time
        self.print_time = 0 # units of minutes

        # internal recording of time at each motion
        self.t = vec(length=int(preallocate))

        # recording the print speed
        self.print_speed = 0

        # Contains names of all the method in GCODE
        self.gcode_methods = {'G0':self.rapid_move,'G1':self.move,'G4':self.dwell,
                              'G20':self.use_in,'G21':self.use_mm,'G28':self.go_home,
                              'G90':self.abs_move,'G91':self.rel_move,
                              'M83':self.abs_extrude,'M82':self.rel_extrude,
                              'M790':self.new_layer,';':self.comment}

        # end of init
        return



    ######################################################################################
    ## GCODE Commands--------------------------------------------------------------------
    ## ------------------------------------------------------------------------------------
    ######################################################################################

    

    # writes line of code with command Gl stright line motion
    def move(self, x=None,y=None,z=None,speed=None,extrude=None,check_end=None,com=None):
        '''
        Parameters:

        > X: The x coordinate to move the print head to. X can be an int,float, or array
            of shape (n,) or (n,3). If shape is (n,), then each element is used
            sequentially as the x coordinate for each motion (each element in the array).
            If X has shape (n,3), then each column is defined as x,y,z and each row is a
            subsequent movement.
        > Y: the y coordinate to move the print head to. Behaves the same as X except for
            that only arrays of shape (n,) can be passed.
        > Z: the z coordinate to move the print head to. Behaves the same as X except for
            that only arrays of shape (n,) can be passed.
        > SPEED: The speed to move the print head for this motion. This input should
            be in the same units as the attribute UNIT_SYS
        > EXTRUDE: The volume to extrude for this motion.... NEED MORE HERE
        > CHECK_END: determines whether the printer checks if an endstop was hit. Default
            to '0'. Options are '0', '1','2'. '1' makes printer check. '2' is more
        > COM: The comment to be added at the end of the lines
        '''

        # checking if x input is a a single value, or an array
        shape = np.shape(x)
        if len(shape) == 2:

            # (n,3) array x is broken into x,y,z components
            if shape[1] == 3:
                y = x[:,1]
                z = x[:,2]
                x = x[:,3]
            else:
                raise ValueError('The input array must have shape (n,3) or (n,) but has shape {}'.format(shape))


        # create a temperary variable to store position to eventually pass to
        # hidden methods to internally record motion
        pos = np.zeros(3)

        # checking if given numerical intputs are single values
        if isinstance(x,int) or isinstance(x,float) or isinstance(y,int) or isinstance(y,float) or isinstance(z,int) or isinstance(z,float):

            # creating line of GCODE
            line = gcode_line('G1', com)

            # calling hidden function to do the string formatting
            # This command writes the gcode line to memory
            self._move_format(line,pos,
                              x,y,z,
                              speed,extrude)
            
            
            # end of move

        else:
            # array case
            if len(x) == len(y) and len(x) == len(z):
                
                # Creating GCODE line for all row in x
                for i in range(len(x)):

                    # creating line of GCODE
                    line = gcode_line('G1', com)
                    
                    # calling hidden function to do the string formatting
                    # This command writes the gcode line to memory
                    self._move_format(line,pos,x[i],y[i],z[i],speed,extrude)

                return                      
    # end of move

    

    # allowing for modelity in GCODE same as move but only write x,y,z
    def simple_move(self, x=None,y=None,z=None):
        '''
        Parameters:

        See Move for X,Y,Z
        
        '''

        # checking if x input is a a single value, or an array
        shape = np.shape(x)
        if len(shape) == 2:

            # (n,3) array x is broken into x,y,z components
            if shape[1] == 3:
                y = x[:,1]
                z = x[:,2]
                x = x[:,3]
            else:
                raise ValueError('The input array must have shape (n,3) or (n,) but has shape {}'.format(shape))

        # create a temperary variable to store position to eventually pass to
        # hidden methods to internally record motion
        pos = np.zeros(3)

        # checking if given numerical intputs are single values
        if isinstance(x,int) or isinstance(x,float) or isinstance(y,int) or isinstance(y,float) or isinstance(z,int) or isinstance(z,float):

            # creating an empty line of GCODE
            line = gcode_line()

            # calling hidden function to do the string formatting
            # this writes this to memory
            self._move_format(line,pos,x,y,z)

            # end of move

        else:

            # array case
            if len(x) == len(y) and len(x) == len(z):

                # Creating GCODE line for all row in x
                for i in range(len(x)):

                    # creating line of GCODE
                    line = gcode_line()
                    
                    # calling hidden function to do the string formatting
                    self._move_format(line,pos,x[i],y[i],z[i])

                                                    
    # end of simple_move


    # method that tells the print to move to X,Y,Z at the max speed
    def rapid_move(self, x=None,y=None,z=None,extrude=None,com=None):
        '''
        Parameters:

        See move except for speed which is automatically set here
        '''

        # chacking if x input is
        shape = np.shape(x)
        if len(shape) == 2:

            # (n,3) array x is broken into x,y,z components
            if shape[1] == 3:
                y = x[:,1]
                z = x[:,2]
                x = x[:,3]
            else:
                raise ValueError('The input array must have shape (n,3) or (n,) but has shape {}'.format(shape))


        # create a temperary variable to store position to eventually pass to
        # hidden methods to internally record motion
        pos = np.zeros(3)

        # checking if given numerical intputs are single values
        if isinstance(x,int) or isinstance(x,float) or isinstance(y,int) or isinstance(y,float) or isinstance(z,int) or isinstance(z,float):

            # creating line of GCODE
            line = gcode_line('G1', com)
            
            # calling hidden function to do the string formatting
            # which also writes to memory
            self._move_format(line,pos,x,y,z,extrude)
            
            # end of move

        else:
            # array case, 
            if len(x) == len(y) and len(x) == len(z):

                # Creating GCODE line for all row in x
                for i in range(len(x)):

                    # creating line of GCODE
                    line = gcode_line('G1', com)

                    # calling hidden function to do the string formatting
                    self._move_format(line,pos,
                                      x[i],y[i],z[i],
                                      extrude)
            else:
                raise ValueError('Input arrays must be of same length')

                return                
                                            
    # end of move


    # method that tells printer to dwell for a specified amount of time
    # this adds s line to motion history and time. This is the current position
    # but the time vector stores the given time at this location
    def dwell(self, sec=None, milisec=None, com=None):
        '''
        Parameters:

        > SEC: the time to wait in seconds
        > MILISEC: the time to wait in miliseconds

        * Notes: SEC takes is defaulted to if both are given. Please only use
            one though!
        '''

        # creating GCODE command 
        line = gcode_line('G4',com)

        # adding the time to wait
        if sec:
            # generating the length of time
            line.append('S{}'.format(sec))

            # writing to memory with time in units of minutes
            self.write(line, self.current_pos, time/60)
            return

        elif:
            # generating length of time
            line.append('P{}'.format(milisec))
            
            # writing to memory with time in units of minutes
            self.write(line, self.current_pos, time/(60*1000))

            return
        else:
            raise RuntimeError('No time given to dwell')
    
        

    def use_mm(self, com='set units to millimeters'):

        # create the gcode line and the comment
        line = gcode_line('G21', com)

        # internally recording the distance units
        self.unit_sys = 'mm'

        # writing the line to memory
        self.write(line)
        return

    def use_in(self, com='set units to inches'):

        # creates the line of gcode with inches command and comment
        line = gcode_line('G20', com)

        # internally recording unit system
        self.unit_sys = 'in'

        # writing to memory
        self.write(line)
        return


    # method to give command to tell printer to use absolute coordinates
    # to move
    def abs_move(self, com='Use Absolute motion'):

        # create gcode line with command and comment
        line = gcode_line('G90', com)

        # internally recording coordinate system
        self.coords = 'abs'

        # writing line of gcode to memory
        self.write(line)
        return
    

    # method to give command to tell printer to use relative coordinates
    # to move
    def rel_move(self, com='Use Relative Motion'):

        # create gcode line with command and comment
        line = gcode_line('G91', com)

        # internally recording coordinate system
        self.coords = 'rel'

        # writing line of gcode to memory
        self.write(line)
        return

    # Method to tell printer to use absolute extrusion
    def abs_extrude(self, com='Absolute Extrusion Mode'):

        # create gcode command
        line = gcode_line('M83', com)

        # should I record the volume used?
        
        # writing line gcode to memory
        self.write(line)
    

    # Method to tell printer to use relative extrusion
    def rel_extrude(self, com='Relative Extrusion Mode'):

        # create gcode command
        line = gcode_line('M82', com)

        # should I record the volume used?
        
        # writing line gcode to memory
        self.write(line)
        

    # adds a new layer
    def new_layer(self, com='announce new layer'):
        line = gcode_line('M790', com)

        # writing to memory
        self.write(line)
        return

    # end of new_layer
    
        
    # writes command for comments
    def comment(self, com):
        '''
        Parameters

        > COM: a string to be written as a comment
        '''
        line = gcode_line(comment=com)

        # writing to memory
        self.write(line)
        return
        # end of comment

    # command that moves specific printer axes to their home position
    def go_home(self, safe=True, x=None,y=None,z=None,com='Going to home position'):
        '''
        Parameters:

        > X,Y,Z: 
        > COM: the comment on the line
        > SAFE: Default is true. This uses a relatively safer way of moving
            home by raising the Z axis first to avoid hitting anything,
            then returning home. CAUTION: This switches to relative coordinates.
            if 
        '''

        # using the safe algorithm
        if safe:

            # using relative motion
            if self.coord_sys == 'abs':
                self.rel_coords()

            # going home by raising z
            line = gcode_line('G28', com)
            
            # ensuring z has acceptable values values
            if z > 0:
                pass
                # raises the 

            # ensuring z has good values
            if not z or z <= 0:

                # move z a different height based on type of units
                if self.coord_sys == 'mm':
                    z = 10
                else:
                    z = 4
                
        else:
            # command to set the home position
            line = gcode_line('G28', com)

            if x:
                line.append('X' + self.settings['pos'].format(x))
            if y:
                line.append('Y' + self.settings['pos'].format(y))
            if z:
                line.append('Z' + self.settings['pos'].format(z))

            # recording line to mem and indicating that this is a move to write
            self.write(line, -self.current_pos)
            # end of go home
        return


    # method that creates blank lines on the GCODE file
    def blank(self, lines=1):

        # checking the lines
        lines = int(lines)

        # creating black lines
        for i in range(lines):
            # determining how to return values
            self.write(gcode_line())

        # end of blank
        return
        
    
    # Adds the credits 
    def credits(self, in_gcode=False):

        line1 = 'This is GCODE generated with gcody version 0.1.5'
        line2 = 'Written by Ryan Zambrotta'
        
        # Writes the credits as a comment
        if in_gcode:
            self.comment(line1)
            self.comment(line2)
        else:
            print(line1)
            print(line2)

        # end of credits
        return

    ######################################################################################
    ######################################################################################
    ## Visualisation tools, Save to memory tools, Saving Tools, Calc Print time---------
    ## ------------------------------------------------------------------------------------
    ######################################################################################
    ######################################################################################
    

    ## IMPORTANT function here. write writes a line to memory as well as parses
    def write(self, line, move=None, time=None):

        '''
        Parameters:

        > LINE:
        > MOVE:
        > TIME:
        '''

        # increasing counter 
        self.count +=1

        # checking debug mode
        # determining how to return values
        if self.debug:
            print(line)
            return
        else:
            # appending the line of GCODE to the vector of lines
            if np.any(move) or np.any(move == 0):
                # records motion, time to print, and position
                self._pos_update(move, time)

                
            # records GCODE
            self.code.append(line.done())
            return    

        # end of write 
        return    

    # method to print the print_time attribute in a pretty format
    # uses a helper function min2time
    # this breaks the attribute print_time into days,hours,minutes, etc.
    def time(self, printit=True, sec_tol=1e-1):
        
        '''
        Parameters:

        > PRINTIT: if true, the final string created is printed to screen and returned.
            If false, then the string is just returned
        > SEC_TOL: controls the precision of the seconds displayed as well as
            whether seconds will be added at all. if the number of seconds is below
            SEC_TOL, then it is not displayed. if more than 2 decimal places are needed
            scientific notation is used
        '''

        # calling helper function
        return min2time(self.print_time, printit, sec_tol)
    # end of time
        

    # Method to visualize the printer path
    '''
    To Do:

    > DOCUMENTATION!!!!
    > Create more arguments for customizability
    > new type of visualization! one color to specify when extrude
        another color not with a legend
    > break this into several methods
    '''
    def view(self, *args, backend='matplotlib', fig_title='Print Path',
             give=False, plot_style='default',**kwargs):
        
        '''
        Parameters:
        

        > BACKEND: str (default: 'matplotlib')
            The plotting backend to use, one of 'matplotlib' or 'mayavi'.
            
        > *args,**kwargs : are passed to matplotlib's pyplot.plot function
        
        > FIG_TITLE: the title given to the figure. Only used is a figure is not given to plot on
        
        > GIVE : this command makes the method return the figure after the path data is
                plotted. This has no effect when mayavi is the backend.
        '''

        # function call from module visual
        plot3(self.history.data(), *args, **kwargs)


        return


    # method that has a colorbar to parameterize the time of the print
    def cbar_view(self, *args, **kwargs):
        '''
        Parameters:
        
        '''

        # function call from module visual
        color_view(self.history.data(), self.t.data(), *args, **kwargs)
        
        
        
        return

    # a function to wrap the stuff needed for a live graph takes a function that returns a
    # X and Y array to be plotted, a single input i to that function is required
    def animated(self, *args, save_file=None, writer='pillow',refresh=100,
                  plot_style='default',show=True,**kwargs):

        '''
        Parameters:

        > SAVE_FILE:
        > ANIMATE:
        > COLOR:
        > REFRESH:
        > PLOT_STYLE:
        '''

        # defining the update function to needed by the plotting function
        def update(i):
            return self.history[0:i,0], self.history[0:i,1], self.history[0:i,2]


        return

    
    # method that has a slider on the bottom of the figure to animate the print path
    def slide_view(self, *args, **kwargs):

        # defining the update function to needed by the plotting function
        def update(i):
            return self.history[0:int(i),0], self.history[0:int(i),1], self.history[0:int(i),2]

        slider_view(update, *args,**kwargs)
        
        return

        

    
    # writes the output to a file
    def save(self, file, ext='gcode'):

        # save file name
        save_file = file + '.' + ext

        # opening and creating file
        with open(save_file,'w') as f:

            # writes all the GCODE lines at once
            f.writelines(self.code)
            
            # closing text file
            f.close()

        # end of store
        return


    ######################################################################################
    ######################################################################################
    ## Hidden methods to handle internal processes---------------------------------------
    ## ------------------------------------------------------------------------------------
    ######################################################################################
    ######################################################################################

    # hidden method to format the GCODE move command
    def _move_format(self, line,pos,x,y,z,speed=None,extrude=None,check_end=None,write=True):
        '''
        Parameters:

        > LINE: the gcode_line that already contains the GCODE command

        > X: The x coordinate to move the print head to. X can be an int,float, or array
            of shape (n,) or (n,3). If shape is (n,), then each element is used
            sequentially as the x coordinate for each motion (each element in the array).
            If X has shape (n,3), then each column is defined as x,y,z and each row is a
            subsequent movement.
        > Y: the y coordinate to move the print head to. Behaves the same as X except for
            that only arrays of shape (n,) can be passed.
        > Z: the z coordinate to move the print head to. Behaves the same as X except for
            that only arrays of shape (n,) can be passed.
        > SPEED: The speed to move the print head for this motion. This input should
            be in the same units as the attribute UNIT_SYS
        > EXTRUDE: The volume to extrude for this motion.... NEED MORE HERE
        > CHECK_END: determines whether the printer checks if an endstop was hit. Default
            to '0'. Options are '0', '1','2'. '1' makes printer check. '2' is more
            machine specific.
        > WRITE: determines whether to write the line to memory or two return the pos and
            line instead
        '''

        # appending parameters to line of GCODE
        if x or x == 0:
            line.append('X' + self.settings['pos'].format(x) )
            # updating position
            pos[0] = x
            
        if y or y == 0:
            line.append('Y' + self.settings['pos'].format(y))
            # updating position
            pos[1] = y
            
        if z or z == 0:
            line.append('Z' + self.settings['pos'].format(z))
            # updating position
            pos[2] = z

        # writes the speed command
        if speed:
            # calls a hidden function to format the speed string
            # and two adjust attributes
            line.append('F' + self._speed(speed))

        # writes the extrusion command to this line
        if extrude:
            line.append('E' + self.settings['extrude'].format(extrude))

        # writes command to check if an end point was hit. this defaults to not checking
        if check_end:
            line.append('S'+check_end)
            
        # determining how to return values or to save the GCODE lines to memory
        if write:
            # writing to memory
            self.write(line,pos)
        else:
            # returning both values
            return line, pos


    
    # method to format the speed command for the move functions and recording the
    # speed as an internal attribute unit_sys.
    def _speed(self, v):
        
        # update internal record of speed
        if self.unit_sys == 'mm':
            # convert units of milimeters per sec to milimeters per minute
            self.print_speed = mmps2mmpm(v)
        else:
            # convert units of inches per sec to inches per meter
            self.print_speed = inps2inpm(v)

        # returning the formated string of the speed
        return self.settings['speed'].format(self.print_speed)


    
    # method to internally record the time for motion. called in _pos_update
    def _time(self, time=None):

        '''
        Calculates the time of motion, independant of coordinate systems

        Parameters:

        > TIME: if time is given, this time is added to the running total
            and to the 
        '''
    
        # distance is the 2-norm distance between the two points
        distance = np.linalg.norm(self.current_pos - self.previous_pos)

        # checking if print_speed has been set to non_zero
        if self.print_speed != 0:

            # if time is given, the value is added, not calculated
            if time:
                self.print_time += time
            else:
                # recording the time taken to move in minutes
                self.print_time += distance/self.print_speed

        # if not, a warning is raised that time will be inf
        else:
            # only printing warning once
            if self.count == 1:
                raise Warning('Print speed not set. Print Times are Inf')

        # adds an element to a vector of time
        self.t.append(self.print_time)
        
        return
    


    # method to internally handle updating the previous and current position, the
    # to the time to move, and recording the history of motion for plotting
    def _pos_update(self, pos, time=None):
        '''
        Parameters:

        > POS: the newly moved to position.  This is always recorded in absolute
            coordinates
        '''

        # reassigning positions of the print head based on motion given by po
        self.previous_pos = self.current_pos.copy() # passing array by copy
        
        # addds the current position to the motion history
        if self.coords == 'abs':

            # recording new position
            self.current_pos = pos
            
        else:
            # records position for relative coordinates. Position is in abs coordinates
            self.current_pos += pos
        
        # recording motion 
        self.history.append(self.current_pos)
        
        # updates the time taken to move the print head
        self._time(time)

        return

    # functions that give the printing options of the GCODE 
    def __repr__(self):
        # creates a print object and returns that 
        return ''.join(self.code)
    
    def __str__(self):
        # creates a print object and returns that
        return ''.join(self.code)

    # gives [] indexing gives access to the gcode methods as identified by the
    # actual GCODE commands. This makes reading GCODE easier
    def __getitem__(self, index):
        return self.gcode_methods[index]

    # gives built in len function access to self.code
    def __len__(self):
        return self.count