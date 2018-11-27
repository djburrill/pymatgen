# coding: utf-8
# Copyright (c) Pymatgen Development Team.
# Distributed under the terms of the MIT License.

__author__ = "Daniel Burrill"
__copyright__ = "Copyright 2018, The Materials Project"
__version__ = "0.1"
__email__ = "djb145@pitt.edu"

# Imports
import re
import numpy as np

class siestaOutput:
    '''
    Reads outfile from SIESTA calculation.
    '''

    def __init__(self,fileName):
        '''
        Constructor.

        INPUT
            fileName: (str) Name of siesta output file (with path).
        '''

        # Read contents of file
        with open(fileName,'r') as inFile:
            self.fileLines = inFile.read()

        # Initialize data
        self.data = {}

        # Read data
        self._read_element_labels()
        self._read_total_energy()
        self._read_optimized_coords()

    def _read_total_energy(self):
        '''
        Read final total energy (in eV).
        '''

        # Variables
        reEnergy = 'siesta:\s+Total\s+=.*'

        # Look for species labels
        energyLine = re.findall(reEnergy,self.fileLines)

        # Update data
        self.data['total_energy'] = float(energyLine[0].split()[-1])

    def _read_element_labels(self):
        '''
        Read labels of the elements so that the user can tell which elements are used in the calculation.
        '''

        # Variables
        reSpec = 'Species\s+number:.*'
        labelDict = {}

        # Look for species labels
        labels = re.findall(reSpec,self.fileLines)

        for label in labels:
            # Format line
            label = label.split()

            # Add label
            labelDict[int(label[2])] = label[-1]

        # Update data
        self.data['labels'] = labelDict

    def _read_optimized_coords(self):
        '''
        Read relaxed structure from siesta output file lines.
        '''

        # Variables
        reVectors = 'outcell: Unit cell vectors.*\n(?:\s+[- ]\d+.\d+\s+[- ]\d+.\d+\s+[- ]\d+.\d+\n)*'
        reAtoms = 'outcoor: Relaxed atomic coordinates.*\n(?:\s+[- ]\d+.\d+\s+[- ]\d+.\d+\s+[- ]\d+.\d+\s+\d+\s+\d+\s+\w+\n)*'

        # Get unit cell vectors
        vecLines = re.findall(reVectors,self.fileLines)

        a = [float(val.split()[0]) for val in vecLines[0].split('\n')[1:-1]]
        b = [float(val.split()[1]) for val in vecLines[0].split('\n')[1:-1]]
        c = [float(val.split()[2]) for val in vecLines[0].split('\n')[1:-1]]

        a = np.asarray(a)
        b = np.asarray(b)
        c = np.asarray(c)

        # Get atomic positions
        atomLines = re.findall(reAtoms,self.fileLines)
        coordList = [np.asarray([float(coord.split()[0]),float(coord.split()[1]),float(coord.split()[2])]) for coord in atomLines[0].split('\n')[1:-1]]
        elementList = [coord.split()[5] for coord in atomLines[0].split('\n')[1:-1]]

        # Update data
        self.data['abc'] = [a,b,c]
        self.data['coordinates'] = coordList
        self.data['elements'] = elementList
