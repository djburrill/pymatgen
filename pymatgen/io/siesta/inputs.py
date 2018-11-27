# coding: utf-8
# Copyright (c) Pymatgen Development Team.
# Distributed under the terms of the MIT License.

__author__ = "Daniel Burrill"
__copyright__ = "Copyright 2018, The Materials Project"
__version__ = "0.1"
__email__ = "djb145@pitt.edu"

# Imports
import pymatgen.core.periodic_table as pmg_pt

class siestaInput:
    '''
    Class for operting on a SIESTA input file. The input file is composed of a couple types of sections:
        1. Keywords. Added using a dictionary keyword where the key is the variable to change and the map is the value to set it to. (ex. {'MaxSCFIterations':200})
        2. Blocks. Blocks are added similarly to keywords using a dictionary structure except that the maps are lists where each element denotes a line. (ex. {'Geometry.Constraints':['atom 1 4 5']})
    '''

    def __init__(self,structure,keywords,blocks):
        '''
        Constructor to set up the input.

        INPUTS
            structure: (pymatgen structure) Structure to use during the calculation.

            keywords: (dict) Dictionary denoting the keywords to alter within the input.

            blocks: (dict) Dictionary denoting blocks to alter within the input.
        '''

        # Set variables
        self.structure = structure
        self.keywords = keywords
        self.blocks = blocks

    def __str__(self):
        '''
        Produce string version of input file.
        '''

        # Variables
        outStr = '### Keywords ###\n'

        # Unpack keywords
        for key in self.keywords:
            outStr += key + ' ' + self.keywords[key] + '\n'

        # Unpack blocks
        outStr += '\n### Blocks ###\n'

        for key in self.blocks:
            outStr += r'%block ' + key + '\n'

            for line in self.blocks[key]:
                outStr += line + '\n'

            outStr += r'%endblock ' + key + '\n'

        # Structure
        outStr += '\n### Structure ###\n'

        outStr += self.atom_block(self.structure)

        return outStr

    def write_file(self,fileName):
        '''
        Write siesta input file.

        INPUTS
            fileName: (str) Name of file to write.
        '''

        with open(fileName,'r') as outFile:
            outFile.write(self.__str__())

    @staticmethod
    def get_species(structure):
        '''
        Return a list of the species in a structure.
        '''

        return [site['species'][0]['element'] for site in structure.as_dict()['sites']]

    def atom_block(self,structure):
        '''
        Create block of atoms.
        '''

        outStr = 'AtomicCoordinatesFormat Fractional\n'
        outStr += 'LatticeConstant 1.0 Ang\n'

        uniqueSpeciesList = list(set(self.get_species(self.structure)))
        nAtoms = len(self.structure.as_dict()['sites'])
        nSpecies = len(uniqueSpeciesList)

        outStr += 'NumberOfAtoms ' + str(nAtoms) + '\n'
        outStr += 'NumberOfSpecies ' + str(nSpecies) + '\n'
        outStr += '\n'

        a = self.structure.as_dict()['lattice']['a']
        b = self.structure.as_dict()['lattice']['b']
        c = self.structure.as_dict()['lattice']['c']

        alpha = self.structure.as_dict()['lattice']['alpha']
        beta = self.structure.as_dict()['lattice']['beta']
        gamma = self.structure.as_dict()['lattice']['gamma']

        outStr += '%block LatticeParameters\n'
        outStr += str(a) + ' ' + str(b) + ' ' + str(c) + ' ' + str(alpha) + ' ' + str(beta) + ' ' + str(gamma) + '\n'
        outStr += '%endblock LatticeParameters\n'
        outStr += '\n'

        outStr += '%block ChemicalSpeciesLabel\n'

        for index,uniqueSpec in enumerate(uniqueSpeciesList):
            ele = pmg_pt.Element(uniqueSpec)
            outStr += str(index+1) + ' ' + str(ele.number) + ' ' + uniqueSpec + '\n'

        outStr += '%endblock ChemicalSpeciesLabel\n'
        outStr += '\n'

        outStr += '%block AtomicCoordinatesAndAtomicSpecies\n'

        for site in self.structure.as_dict()['sites']:
            a_a = str(site['abc'][0])
            a_b = str(site['abc'][1])
            a_c = str(site['abc'][2])
            specNum = str(1+uniqueSpeciesList.index(site['species'][0]['element']))

            outStr += a_a + ' ' + a_b + ' ' + a_c + ' ' + specNum + '\n'

        outStr += '%endblock AtomicCoordinatesAndAtomicSpecies\n'

        return outStr
