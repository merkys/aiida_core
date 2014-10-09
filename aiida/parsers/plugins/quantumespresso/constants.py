# -*- coding: utf-8 -*-
"""
Physical or mathematical constants. 
Since every code has its own conversion units, this module defines what
QE understands as for an eV or other quantities.
"""

__author__ = "Giovanni Pizzi, Andrea Cepellotti, Riccardo Sabatini, Nicola Marzari, and Boris Kozinsky"
__copyright__ = u"Copyright (c), 2012-2014, École Polytechnique Fédérale de Lausanne (EPFL), Laboratory of Theory and Simulation of Materials (THEOS), MXC - Station 12, 1015 Lausanne, Switzerland. All rights reserved."
__license__ = "MIT license, see LICENSE.txt file"
__version__ = "0.2.0"

bohr_to_ang=0.52917720859
ang_to_m=1.e-10
bohr_si = bohr_to_ang * ang_to_m
ry_to_ev=13.6056917253
ry_si = 4.35974394/2. * 10**(-18)
hartree_to_ev = ry_to_ev*2.
timeau_to_sec = 2.418884326155573e-17
invcm_to_THz = 0.0299792458
