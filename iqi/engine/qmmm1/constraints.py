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
from iqi.utils.quit_simulation import *
from iqi.utils.io.io_xml import *
import operator
import numpy as np


class SphereConstraint(object):
    
    def __init__(self, central_atom_id):
        self.central_atom_id = central_atom_id
        self.radius_QC = None
        self.radius_MC = None
        self.contained_atom_ids = []
        self.contained_atom_distances = []
        self.contained_atom_distance_vectors = []


class Constraints(object):
    
    def __init__(self, inputdata, simulation):

        # Instance variables
        self.input_data_splitted = {}
        self.constraints_file_name = None
        self.constraints_data = None
        self.spheres = []
        self.simulation = simulation
        self.sphere_atom_ids = []
        
        # Loop for storing the xml tags of the input data
        for (name, xml_node) in inputdata.fields:
            if name == "file":
                self.input_data_splitted["file"] = xml_node
            elif name is not "_text":
                xml_tag_error("<constraints>", self)
                quit_simulation()
                
        # Initializing the instance variables
        if self.input_data_splitted["file"].attribs["type"] == "xml":
            if self.input_data_splitted["file"].fields[0][0] == "_text":
                self.constraints_file_name = self.input_data_splitted["file"].fields[0][1]
        
        # Preparing the constraints input data as xml tree 
        with open(self.constraints_file_name, "r") as constraints_file:
            # Parsing the input file
            constraints_data = xml_parse_file(constraints_file)
            
        # Creating the sphere constraint objects
        for (name, xml_node) in constraints_data.fields:
            if name == "spheres":
                for (name_2, xml_node_2) in xml_node.fields:
                    if name_2 == "sphere":
                        self.spheres.append(SphereConstraint(xml_node_2.attribs["atom_id"]))
                        self.sphere_atom_ids.append(xml_node_2.attribs["atom_id"])
            elif name != "_name":
                xml_tag_error("constraints file", self)
                quit_simulation()
        
            
    def update(self):
        
        # Resetting the spheres (deleting entries from previous computations), number of atoms may change
        for sphere in self.spheres:
            sphere.contained_atom_ids = []
            sphere.contained_atom_distances = []
            sphere.contained_atom_distance_vectors = []
        
        # Computing the distances between the QC atoms and the sphere centers
        distances, distance_vectors = self.simulation.cell.distances(self.sphere_atom_ids, self.simulation.atoms.atom_ids_QC)
        
        # Associating the constrained QM atoms to their closest spheres
        for i in range(0, self.simulation.atoms.total_number_QC):
            min_index, min_value = min(enumerate(distances[:,i]), key=operator.itemgetter(1))
            self.spheres[min_index].contained_atom_ids.append(self.simulation.atoms.atom_ids_QC[i])
            self.spheres[min_index].contained_atom_distances.append(min_value)
            self.spheres[min_index].contained_atom_distance_vectors.append(distance_vectors[min_index,i,:])

        # Computing the radii of the spheres
        for sphere in self.spheres:
            sphere.radius_QC = max(sphere.contained_atom_distances)