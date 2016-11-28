"""
Summary:


Copyright (C) 2016, Christoph Gorgulla

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http.//www.gnu.org/licenses/>.



"""

import sys
from iqi.utils.io.io_xml import *
from iqi.engine.simulation import Simulation
from iqi.utils.messages import * 


def main(file_name):

    # Preparing the input data as xml tree 
    with open(file_name, "r") as inputfile:
        # Parsing the input file
        inputdata = xml_parse_file(inputfile)

    # Displaying program logo
    if inputdata.fields[0][1].attribs["verbosity"] != "quiet":
        program_heading()

    # Creating the simulation object
    simulation = Simulation(inputdata.fields[0][1])

    # Displaying initial information
    if simulation.verbosity.low:
        print "i-QI has being started"
        print "The input file used is: "+ file_name
        
    # Displaying the input file
    if simulation.verbosity.medium:
        print "\n *****  Beginning of Input file content  ***** "
        with open(file_name, "r") as inputfile:
            for line in inputfile.readlines():
                print line,
        print "\n *****   End of input file content   ***** "
    
    # Running the simulation
    simulation.run()
    

# Checking if this file is run as the main program 
if __name__ == '__main__':
    
    # Checking the number of arguments 
    if (len(sys.argv) != 2):
        help()
    else:
        main(sys.argv[1])
