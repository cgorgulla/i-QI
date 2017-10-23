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
from iqi.utils.messages import *
from iqi.utils.quit_simulation import *
import numpy as np

class Atoms(object):
    # Atom ID is atom index of atom (according to the position when reading in the input pdbx file), first index is 0. But only internally. The index we specify externally in the constraints file start at 1 (position in pdbx file), we substract automatically "1"
    
    def __init__(self, inputdata, simulation):
        
        # Instance variables
        # Basic
        self.simulation = simulation
        self.inputdata = inputdata
        self.file_type = None
        self.file_name = self.filename() 
        self.total_number = np.int32(self.no_of_atoms())
        self.atom_ids_QC = []
        self.atom_ids_MC = []
        self.positions = np.zeros((self.total_number,3))
        # Molecule information
        self.atom_to_chain = []
        self.atom_to_residue = []
        self.atom_to_molecule = []
        self.molecule_names = set()
        self.molecule_to_atoms = {}

        # Determining the atom types
        self.atom_types()
        self.total_number_QC = len(self.atom_ids_QC)
        self.total_number_MC =  len(self.atom_ids_MC)

        # Preparing the molecule information
        self.prepare_molecules()


    def filename(self):
        if self.inputdata.fields[0][0] == "type":
            node_atom_type = self.inputdata.fields[0][1]
            if node_atom_type.fields[0][0] == "file":
                node_atom_type_file = node_atom_type.fields[0][1]
                if "type" in node_atom_type_file.attribs:
                    self.file_type = node_atom_type_file.attribs["type"]                    
                    if node_atom_type_file.fields[0][0]== "_text":
                        return node_atom_type_file.fields[0][1].strip()
                    else:
                        xml_tag_error("<file> (within the <atoms><type> section)", self.simulation)        
                else:
                    xml_tag_error("<file> (within the <atoms><type> section)", self.simulation)
            else:
                xml_tag_error("<file> (within the <atoms><type> section)", self.simulation)
        else:
            xml_tag_error("<type> (within the <atoms> section)", self.simulation)
    
    
    def no_of_atoms(self):
    
        if self.file_type == "pdbx":
            with open(self.file_name, "r") as pdbxfile:
                total_number = 0
                for line in pdbxfile:
                    if "ATOM" in line or "HETATM" in line:
                        total_number += 1
            return total_number
        else:
            info("Unsupported file format specified in input-file.",  self.simulation.verbosity.quiet)
            quit_simulation()


    def atom_types(self):
        atom_id = 0
        if self.file_type == "pdbx":
            with open(self.file_name, "r") as inputfile:
                for line in inputfile:
                    if "ATOM" in line or "HETATM" in line:     
                        atom_type = line[80:82]
                        if atom_type in "QC":
                            self.atom_ids_QC.append(atom_id)
                        elif atom_type in "MC":
                            self.atom_ids_MC.append(atom_id)
                        elif atom_type not in ["MU", "QU"]:
                            info("Unsupported atom type scecified in the file " + self.file_name, self.simulation.verbosity.quiet)
                            info("Specified atom type: " + atom_type + " in atom with index " + atom_id, self.simulation.verbosity.quiet)
                            quit_simulation()
                        atom_id += 1

                        # Molecule information
                        chain = line[21]
                        residue = line[22:26].strip()
                        if chain == "R" or chain == "L":
                            molecule = chain
                        elif chain == "W":
                            molecule = chain + residue
                        else:
                            raise ValueError('Unsupported chain identifyer (' + chain + ') found in the input pdbx file. Supported are only R, L and W.')
                        self.atom_to_molecule.append(molecule)


    def prepare_molecules(self):

        # Creating the set of names of all molecules
        self.molecule_names = set(self.atom_to_molecule)

        # Filling the molecule_to_atoms dictionary with the molecule names
        for molecule_name in self.molecule_names:
            self.molecule_to_atoms[molecule_name] = set()

        # Adding the atoms to the molecule_to_atoms dictionary
        for atom_index in range(1, self.total_number, 1):
            molecule=self.atom_to_molecule[atom_index]
            self.molecule_to_atoms[molecule].add(atom_index)


