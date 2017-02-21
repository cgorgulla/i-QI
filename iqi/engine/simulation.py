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

from iqi.engine.atoms import *
from iqi.interfaces.serverinterface import * 
from iqi.engine.cell import *
from iqi.interfaces.socketinterface import SocketInterface
from iqi.utils.quit_simulation import *
from enum import Enum

class Simulation(object):
    
    Status = Enum("Status", "needinit ready havedata exiting")
    
    def __init__(self, inputdata):
        
        # Instance variables
        self.verbosity = None
        self.status = self.Status.needinit
        self.atoms = None
        self.cell = Cell(self)
        self.server_interface = None
        self.potential = None
        self.input_data_splitted = {}

        # Printing verbosity information
        if "verbosity" in inputdata.attribs:
            self.verbosity = Verbosity(inputdata.attribs["verbosity"])
            info("Setting verbosity to level \"" + inputdata.attribs["verbosity"] + "\"", self.verbosity.medium)
        else:
            self.verbosity = Verbosity()
            info("No verbosity level specified. Setting verbosity to the default value (" + str(Verbosity.VERB_DEFAULT) + ")", verbosity.medium)
        
        # Loop for storing the inner xml tags of the input data
        for (name, xml_node) in inputdata.fields:
            if name == "interface":
                self.input_data_splitted["interface"] = xml_node
            elif name == "atoms":
                self.input_data_splitted["atoms"] = xml_node
            elif name == "potential":
                self.input_data_splitted["potential"] = xml_node                     
            elif name is not "_text":
                xml_tag_error("<simulation>", self)
                quit_simulation()
        
        # Initializing the instance variables
        # Initializing the interface to the server
        if self.input_data_splitted["interface"].attribs["type"] == "socket":               
            self.server_interface = SocketInterface(self.input_data_splitted["interface"], self)
        # Initialzing the atoms object
        self.atoms = Atoms(self.input_data_splitted["atoms"], self)
        # Initializing the potential
        if self.input_data_splitted["potential"].attribs["type"] == "QMMM1":
            import iqi.engine.qmmm1.qmmm1
            self.potential = iqi.engine.qmmm1.qmmm1.QMMM1(self.input_data_splitted["potential"], self)
    
    # Method for running the simulation         
    def run(self):
        
        while True:
            message = self.server_interface.recv_message()
            
            if message == InterfaceMessages.IN_STATUS:                
                if self.status == self.Status.needinit:
                    self.server_interface.send_message(InterfaceMessages.OUT_NEEDINIT)
                elif self.status == self.Status.havedata:
                    self.server_interface.send_message(InterfaceMessages.OUT_HAVEDATA)
                elif self.status == self.Status.ready:
                    self.server_interface.send_message(InterfaceMessages.OUT_READY)
                    
            elif message == InterfaceMessages.IN_INIT:      
                self.server_interface.recv_init()
                self.status = self.Status.ready
            
            elif message == InterfaceMessages.IN_POSDATA:
                self.cell.cell_matrix, self.cell.cell_matrix_inverse, self.atoms.positions = self.server_interface.recv_data(self.cell.cell_matrix, self.cell.cell_matrix_inverse, self.atoms.positions)
                self.cell.cell_size = np.array([self.cell.cell_matrix[0,0], self.cell.cell_matrix[1,1], self.cell.cell_matrix[2,2]], np.float64)
                self.cell.cell_size_invert = 1. / self.cell.cell_size
                self.potential.compute_interactions()
                self.status = self.Status.havedata
                        
            elif message == InterfaceMessages.IN_GETFORCE:               
                self.server_interface.send_message(InterfaceMessages.OUT_FORCEREADY)
                self.server_interface.send_all(self.potential.total_energy, "total energy")
                self.server_interface.send_all(self.atoms.total_number, "number of atoms")
                self.server_interface.send_all(self.potential.forces.flatten(), "forces")
                self.server_interface.send_all(self.potential.pressure_virial_tensor, "virial tensor") # TODO proper shape virial (transpose???)
                self.server_interface.send_all(np.int32(1), "size of extra-string") # size of extra string
                self.server_interface.send_all(" ", "extra string") # extra string
                self.status = self.Status.ready
                
            
            elif message == InterfaceMessages.IN_EXIT:
                self.status = self.Status.exiting
                break
            
            else:
                info("Unrecognized message received from server: " + message, self.verbosity.quiet)
                quit_simulation()