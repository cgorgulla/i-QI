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


Classes:

"""

import sys
from iqi.utils.messages import *

__all__ = ["quit_simulation", "xml_tag_error"]


def xml_tag_error(tag, simulation):
    info("Input file contains errors regarding the xml_tag " + tag, simulation.verbosity.quiet)
    quit_simulation()
    

def quit_simulation():
    
    info("Halting the simulation.", verbosity.quiet)
    sys.exit()