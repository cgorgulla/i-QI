"""
Copyright (C) 2016, Christoph Gorgulla

This file is part of i-QI.

i-QI is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Foobar is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
"""

import numpy as np

class Cell(object):
    
    def __init__(self, simulation):        
        
        self.cell_matrix = np.zeros((3,3))
        self.cell_matrix_inverse = np.zeros((3,3))
        self.cell_size = np.zeros(3,np.float64)
        self.cell_size_invert = np.zeros(3, np.float64)
        self.simulation = simulation
    
    # Atom set 1 are the tips, atom set 2 are the origins
    def distances(self, atom_set_1, atom_set_2):
        
        distances = np.zeros((len(atom_set_1),len(atom_set_2)),np.float64)
        distance_vectors = np.zeros((len(atom_set_1), len(atom_set_2), 3), np.float64)
        
        for atom_1_id in range(0, len(atom_set_1)):
            for atom_2_id in range(0, len(atom_set_2)):
                x1 = self.simulation.atoms.positions[atom_set_1[atom_1_id], :]
                x2 = self.simulation.atoms.positions[atom_set_2[atom_2_id], :]
                dx2x1 = self.distance_vector(x1, x2)
                distance_vectors[atom_1_id, atom_2_id, :] = dx2x1
                distances[atom_1_id, atom_2_id] = np.linalg.norm(dx2x1)
                
        return distances, distance_vectors

    # Distance vector, x1 is the tip, x2 is origin
    def distance_vector(self, x1, x2): 
        # dx1x2 = x1 - x2
        #for i in range(0,len(x1)):
        #    dx1x2[i] -= self.cell_matrix[i,i] * round(dx1x2[i] * self.cell_matrix_inverse[i,i])
        
        # print dx1x2
        dx2x1 = x1 - x2
        dx2x1 -= self.cell_size * np.round(dx2x1 * self.cell_size_invert)
        # print dx1x2
   
        return dx2x1
