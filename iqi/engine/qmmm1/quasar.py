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
        self.pressure_virial_tensor = np.array([[0,0,0],[0,0,0],[0,0,0]], np.float64)
        self.input_data_splitted = {}

        # Loop for storing the inner xml tags of the input data
        for (name, xml_node) in inputdata.fields:
            if name == "constraints":
                self.input_data_splitted["constraints"] = xml_node
            elif name == "forceconstant":
                self.input_data_splitted["forceconstant"] = xml_node
            elif name == "force_distribution":
                self.input_data_splitted["force_distribution"] = xml_node
            elif name is not "_text":
                xml_tag_error("<Potential>", self)
                quit_simulation()

        # Initializing the instance variables
        # Initializing the constraints object
        self.constraints = Constraints(self.input_data_splitted["constraints"], self.simulation)
        # Setting the force constant
        if is_number(self.input_data_splitted["forceconstant"].fields[0][1].strip()):
            self.force_constant = np.float64(self.input_data_splitted["forceconstant"].fields[0][1].strip())
        else:
            xml_tag_error("<force constant>", self)
            quit_simulation()

        # Setting the force distribution
        if self.input_data_splitted["force_distribution"].fields[0][1].strip() == "atom" or self.input_data_splitted["force_distribution"].fields[0][1].strip() == "molecule":
            self.force_distribution = self.input_data_splitted["force_distribution"].fields[0][1].strip()
        else:
            xml_tag_error("<force_distribution>", self)
            quit_simulation()




    # Method for computing the interactions and related properties: forces, potentials, virials
    def compute_interactions(self):

        # Cleaning up past values
        self.forces = np.zeros((self.simulation.atoms.total_number,3), np.float64)
        self.total_energy = np.float64(0)
        self.pressure_virial_tensor = np.array([[0,0,0],[0,0,0],[0,0,0]], np.float64)

        # Updating the constraints
        self.constraints.update()
        
        # Computing the distances of the MC atoms to the sphere centers
        distances_MC_SC, distance_vectors_MC_SC = self.simulation.cell.distances(self.constraints.sphere_atom_ids, self.simulation.atoms.atom_ids_MC)
        
        # Computing the forces on the MC atoms and adding the contributions to the total potential
        for i, sphere in enumerate(self.constraints.spheres):
            for j, atom_id_MC in enumerate(self.simulation.atoms.atom_ids_MC):
                if distances_MC_SC[i,j] < sphere.radius_QC:
                    self.forces[atom_id_MC,:] += - (sphere.radius_QC - distances_MC_SC[i,j]) * (distance_vectors_MC_SC[i,j,:] / distances_MC_SC[i,j]) * self.force_constant
                    self.total_energy += 0.5 * (sphere.radius_QC - distances_MC_SC[i,j])**2 * self.force_constant

                    # Applying the same forces to the entire molecule
                    if self.force_distribution == "molecule":
                        for k, molecule_atom_id in enumerate(self.simulation.atoms.molecule_to_atoms[self.simulation.atoms.atom_to_molecule[atom_id_MC]]):
                            if molecule_atom_id != atom_id_MC:
                                self.forces[molecule_atom_id,:] += - (sphere.radius_QC - distances_MC_SC[i,j]) * (distance_vectors_MC_SC[i,j,:] / distances_MC_SC[i,j]) * self.force_constant
                                self.total_energy += 0.5 * (sphere.radius_QC - distances_MC_SC[i,j])**2 * self.force_constant



        # Computing the outer radius of the spheres
        for i, sphere in enumerate(self.constraints.spheres):
            sphere.radius_MC = min(distances_MC_SC[i, :])

        # Computing the forces and potential on the QC atoms and adding the contributions to the total potential 
        for i, sphere in enumerate(self.constraints.spheres):
            for j, distance in enumerate(sphere.contained_atom_distances):
                if distance > sphere.radius_MC:
                    self.forces[sphere.contained_atom_ids[j],:] += (distance - sphere.radius_MC) * (sphere.contained_atom_distance_vectors[j] / sphere.contained_atom_distances[j]) * self.force_constant
                    self.total_energy += 0.5 * (distance - sphere.radius_MC)**2 * self.force_constant

                    # Applying the same forces to the entire molecule
                    if self.force_distribution == "molecule":
                        for k, molecule_atom_id in enumerate(self.simulation.atoms.molecule_to_atoms[self.simulation.atoms.atom_to_molecule[sphere.contained_atom_ids[j]]]):
                            if molecule_atom_id != sphere.contained_atom_ids[j]:
                                self.forces[molecule_atom_id, :] += (distance - sphere.radius_MC) * (sphere.contained_atom_distance_vectors[j] / sphere.contained_atom_distances[j]) * self.force_constant
                                self.total_energy += 0.5 * (distance - sphere.radius_MC) ** 2 * self.force_constant

        # Computing the pressure virial tensor 
        for i in range(1, self.simulation.atoms.total_number):
            for j in range(1,3,):
                for k in range(j,3):
                    self.pressure_virial_tensor[j,k] = self.pressure_virial_tensor[j,k] + self.forces[i,j]*self.simulation.atoms.positions[i,k]