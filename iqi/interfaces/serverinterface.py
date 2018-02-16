"""
Copyright (C) 2013, Joshua More and Michele Ceriotti
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

__all__ = ["InterfaceMessages", "ServerInterface"]


class InterfaceMessages(object):

    MESSAGE_LENGTH = 12

    # Recognized incoming messages
    IN_INIT = "INIT        "
    IN_STATUS = "STATUS      "
    IN_POSDATA = "POSDATA     "
    IN_GETFORCE = "GETFORCE    "
    IN_EXIT = "EXIT        "
    
    # Outgoing messages
    OUT_NEEDINIT = "NEEDINIT    "
    OUT_READY = "READY       "
    OUT_HAVEDATA = "HAVEDATA    "
    OUT_FORCEREADY = "FORCEREADY  "
        

class ServerInterface(object):
    
    def __init__(self, simulation):
        self.simulation = simulation

    def recv_message(self):
        pass 

    def recv_data(self, cell_size, cell_size_invert, positions):
        pass

    def send_all(self, outgoing_data):
        pass

    def send_message(self, outgoing_data):
        pass