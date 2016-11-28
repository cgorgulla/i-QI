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


class Potential(object):
    def __init__(self, inputdata, simulation):
        
        self.inputdata = inputdata
        self.simulation = simulation
        self.forces = None
        self.constraints = None
        self.total_energy = None
        self.pressure_virial_tensor = None  


    def compute_interactions(self):
  
        pass

