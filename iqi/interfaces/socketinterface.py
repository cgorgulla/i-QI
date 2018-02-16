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

import socket 
from iqi.utils.messages import *
from iqi.interfaces.serverinterface import *
from iqi.utils.quit_simulation import *
import numpy as np

class SocketInterface(ServerInterface, socket.socket):

    def __init__(self, inputdata, simulation):
        
        super(SocketInterface, self).__init__(simulation)
        self.inputdata_socket = inputdata.fields[0][1]
        self.socket_to_server = None
        self.socket_type = self.inputdata_socket.attribs["type"]
        
        #TODO:Automatically closing sockets if program quits unexpectedly
        # http: // stackoverflow.com / questions / 16915023 / python - sockets - how - to - handle - the - client - closing - unexpectedly
        
        if self.socket_type == "inet":
            self.socket_to_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket_to_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.address = None
            self.port = None
            for (name, xml_node) in self.inputdata_socket.fields:
                if name == "address":
                    self.address = xml_node.fields[0][1].strip()
                elif name == "port":
                    self.port = xml_node.fields[0][1].strip()
                elif name != "_text":
                    xml_tag_error("<socket>", simulation)
            
            if self.address is not None and self.port is not None:
                self.socket_to_server.connect((self.address, int(self.port)))
                info("Connected to server via the internet socket with address: " + self.address + ":" + self.port, self.simulation.verbosity.medium)
            else:
                info("The host address and port were not both specified correctly in the input file.", self.simulation.verbosity.quiet)
                quit_simulation()
        
        elif self.socket_type == "unix":
            self.socket_to_server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.socket_to_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.address = None

            for (name, xml_node) in self.inputdata_socket.fields:
                if name == "address":
                    self.address = xml_node.fields[0][1].strip()
                elif name != "_text":
                    xml_tag_error("<socket>", simulation)
            
            if self.address is not None:
                print("/tmp/ipi_" + self.address)
                self.socket_to_server.connect("/tmp/ipi_" + self.address)
                info("Connected to server via unix domain socket with socket path: " + "/tmp/ipi_" + self.address, self.simulation.verbosity.medium)
            else:
                info("The host address was not specified correctly in the input file.", self.simulation.verbosity.quiet)
                quit_simulation()

    def recv_message(self):      
        incoming_data = ""
        data_size_received = 0
        while data_size_received < InterfaceMessages.MESSAGE_LENGTH:
            buffer = self.socket_to_server.recv(InterfaceMessages.MESSAGE_LENGTH - data_size_received)
            buffer = str(buffer)
            incoming_data += buffer
            data_size_received += len(buffer)
        info("Received message from server:" + incoming_data, self.simulation.verbosity.high)
        return incoming_data
    
    def recv_init(self):
    
        # Getting the replica id (rid)
        self.recv_nparray(np.zeros(1, np.int32))

        data_size_expected = self.recv_nparray(np.zeros(1, np.int32))
        data_size_received = 0
        
        extra_string = ""
        while data_size_received < data_size_expected:
            buffer = self.socket_to_server.recv(data_size_expected - data_size_received)
            buffer = str(buffer)
            extra_string += buffer
            data_size_received += len(buffer)
        info("Received the init data from the server: " + extra_string, self.simulation.verbosity.high)


    def recv_data(self, cell_matrix, cell_matrix_invert, positions):

        cell_matrix = self.recv_nparray(cell_matrix, "cell matrix")
        cell_matrix_invert = self.recv_nparray(cell_matrix_invert, "cell matrix inverse")
        self.recv_nparray(np.array(np.int32(1)), "number of atoms") # number of atoms, we don't need
        positions = self.recv_nparray(positions, "atom positions")        
        return cell_matrix, cell_matrix_invert, positions
    
    def recv_nparray(self, nparray, data_name=""):
        
        data_size_expected = nparray.itemsize*nparray.size
        data_size_received = 0
        data_received = ""
        while data_size_received < data_size_expected:
            buffer = self.socket_to_server.recv(data_size_expected - data_size_received)
            data_received += buffer
            data_size_received += len(buffer)
        data_received = np.fromstring(data_received, nparray.dtype)
        nparray = data_received.reshape(nparray.shape, order="C")
        info("Received data from server: " + data_name, self.simulation.verbosity.high)
        return nparray

    def send_all(self, outgoing_data, data_name=""):
        self.socket_to_server.sendall(outgoing_data)
        info("Sent data to server: " + data_name, self.simulation.verbosity.high)

    def send_message(self, message):
        self.socket_to_server.sendall(message)
        info("Sent message to server: " + message, self.simulation.verbosity.high)