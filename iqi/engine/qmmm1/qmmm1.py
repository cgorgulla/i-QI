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
from iqi.engine.potential import * 
from iqi.utils.various import is_number
import numpy as np
from iqi.engine.qmmm1.constraints import *

__all__ = ["QMMM1"]


class QMMM1(Potential):
    
    def __init__(self, inputdata, simulation):
        
        # Initialization of the base class
        super(QMMM1, self).__init__(inputdata, simulation)
        
        # Instance variables
        self.forces = np.zeros((simulation.atoms.total_number,3), np.float64)
        self.constraints = None
        self.total_energy = np.float64(0)
        self.pressure_virial_tensor = np.array([[1,2,3],[0,4,5],[0,0,6]], np.float64)
        self.input_data_splitted = {}

        # Loop for storing the inner xml tags of the input data
        for (name, xml_node) in inputdata.fields:
            if name == "constraints":
                self.input_data_splitted["constraints"] = xml_node
            elif name == "forceconstant":
                self.input_data_splitted["forceconstant"] = xml_node
            elif name is not "_text":
                xml_tag_error("<constraints>", self)
                quit_simulation()

        # Initializing the instance variables
        # Initializing the constraints object
        self.constraints = Constraints(self.input_data_splitted["constraints"], self.simulation)
        # Setting the force constant
        if is_number(self.input_data_splitted["forceconstant"].fields[0][1]): 
            self.force_constant = np.float64(self.input_data_splitted["forceconstant"].fields[0][1])
        else:
            xml_tag_error("<force constant>", self)
            quit_simulation()



    # Method for computing the interactions and related properties: forces, potentials, virials
    def compute_interactions(self):

        # Updating the constraints
        self.constraints.update()
        
        # Computing the distances of the MC atoms to the sphere centers
        distances_MC_SC, distance_vectors = self.simulation.cell.distances(self.constraints.sphere_atom_ids, self.simulation.atoms.atom_ids_MC)
        
        # Computing the forces on the MC atoms and adding the contributions to the total potential 
        for i, sphere in enumerate(self.constraints.spheres):
            for j, atom_id_MC in enumerate(self.simulation.atoms.atom_ids_MC):
                if distances_MC_SC[i,j] < sphere.radius_QC:
                    self.forces[atom_id_MC,:] += (sphere.radius_QC - distances_MC_SC[i,j]) * distance_vectors[i,j,:] * self.force_constant
                    self.total_energy += 0.5 * (sphere.radius_QC - distances_MC_SC[i,j])**2 * self.force_constant

        # Computing the outer radius of the spheres
        for i, sphere in enumerate(self.constraints.spheres):
            sphere.radius_MC = min(distances_MC_SC[i, :])

        # Computing the forces and potential on the QC atoms and adding the contributions to the total potential 
        for i, sphere in enumerate(self.constraints.spheres):
            for j, distance in enumerate(sphere.contained_atom_distances):
                if distance > sphere.radius_MC:
                    self.forces[sphere.contained_atom_ids[j],:] += - (distance - sphere.radius_MC) * (sphere.contained_atom_distance_vectors[j] / sphere.contained_atom_distances[j]) * self.force_constant
                    self.total_energy += 0.5 * (distance - sphere.radius_MC)**2 * self.force_constant
        
       
        # Computing the pressure virial tensor 
        


        
        
    
        
        