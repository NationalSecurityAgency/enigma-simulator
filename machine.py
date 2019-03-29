#!/usr/bin/python

'''
Enigma Machine Simulation
Author: Emily Willson
Date: April 6, 2018

Details: This file holds the code necessary to actually run the Enigma machine simulation. It draws on the components file to provide the constituent parts of the machine and implements a command line interface to operate the encryption process.

Specifications: In particular, this module implements the 3 rotor Enigma machine with plugboard and reflector used by the German army during WWII. It may later be expanded to include a selection of 5 possible rotors, but right now it will use the hardcoded 3 rotor version for the purposes of simplicity.
'''
# Module imports.
import re

from components import Rotor, Plugboard, Reflector, ALPHABET

class Enigma():
    '''
    This class will bring together components to create an actual Enigma machine.

    Thought about geometrically, the Enigma can be viewed as follows:

    Keyboard -> Plugboard -> L Rotor -> M Rotor -> R Rotor -> Reflector.

    The generic initial rotor ordering (which can be changed by the user) is L = I, M = II, R = III (I,II,III are the three Wehrmacht Enigma rotors defined in components.py)
    '''

    def __init__(self, key='AAA', swaps=None, rotor_order=['I', 'II', 'III']):
        '''
        Initializes the Enigma machine.

        key = Three letter string specifying the top/visible letter for the left, middle, and right rotors respectively. This determines indexing in the rotor.

        swaps = Specifies which plugboard swaps you would like to implement, if any. These should be provided in the form [('A', 'B'), ('T', 'G')] if you want to swap A,B and T,G.

        rotor_order = Defines which rotor to set as the left, middle, and right rotors respectively when considering the Enigma geometrically as described above.
        '''
        if len(key) != 3:
            print('Please provide a three letter string as the initial window setting.')
            return None
        # Set the key and rotor order.
        self.key = key
        self.rotor_order = rotor_order
        # Now define the components.
        self.r_rotor = Rotor(rotor_order[2], key[2])
        self.m_rotor = Rotor(rotor_order[1], key[1], self.r_rotor)
        self.l_rotor = Rotor(rotor_order[0], key[0], self.m_rotor)
        self.reflector = Reflector()
        self.plugboard = Plugboard(swaps)
        # Define prev_rotor information for middle and right rotors.
        self.m_rotor.prev_rotor = self.l_rotor
        self.r_rotor.prev_rotor = self.m_rotor

    def __repr__(self):
        print('Keyboard <-> Plugboard <->  Rotor ' + self.rotor_order[0]
              + ' <-> Rotor ' + self.rotor_order[1]
              + ' <-> Rotor ' + self.rotor_order[2]
              + ' <-> Reflector ')
        return 'Key: ' + self.key

    def encipher(self, message):
        """
        Given a message string, encode or decode that message.
        """
        cipher = ''
        # Test the message string to make sure it only contains a-zA-Z
        if bool(re.compile(r'[^a-zA-Z ]').search(message)):
            return 'Please provide a string containing only the characters a-zA-Z and spaces.'
        for letter in message.upper().replace(" ", "").strip():
            cipher += self.encode_decode_letter(letter)
        return cipher

    def decipher(self, message):
        """
        Encryption == decryption.
        """
        return self.encipher(message)

    def encode_decode_letter(self, letter):
        """ Takes a letter as input, steps rotors accordingly, and returns letter output.
        Because Enigma is symmetrical, this works the same whether you encode or decode.
        """
        # Make sure the letter is in a-zA-Z.
        if bool(re.compile(r'[^a-zA-Z ]').search(letter)):
            return 'Please provide a letter in a-zA-Z.'
        # First, go through plugboard.
        if letter in self.plugboard.swaps:
            letter = self.plugboard.swaps[letter.upper()]
        # Next, step the rotors.
        self.l_rotor.step()
        # Send the letter through the rotors to the reflector.
        # Get the index of the letter that emerges from the rotor.
        left_pass = self.l_rotor.encode_letter(ALPHABET.index(letter.upper()))
        # Must match letter INDEX, not letter name to reflector as before. 
        refl_output = self.reflector.wiring[ALPHABET[(left_pass)%26]]
        # Send the reflected letter back through the rotors.
        final_letter = ALPHABET[self.r_rotor.encode_letter(
            ALPHABET.index(refl_output), forward=False)]
        if final_letter in self.plugboard.swaps:
            return self.plugboard.swaps[final_letter]
        else:
            return final_letter

    def set_rotor_position(self, position_key, printIt=False):
        '''
        Updates the visible window settings of the Enigma machine, rotating the rotors.
        The syntax for the rotor position key is three letter string of the form 'AAA' or 'ZEK'.
        '''
        if type(position_key)==str and len(position_key)==3:
            self.key = position_key
            self.l_rotor.change_setting(self.key[0])
            self.m_rotor.change_setting(self.key[1])
            self.r_rotor.change_setting(self.key[2])
            if printIt:
                print('Rotor position successfully updated. Now using ' + self.key + '.')
        else:
            print('Please provide a three letter position key such as AAA.')

    def set_rotor_order(self, order):
        '''
        Changes the order of rotors in the Engima machine to match that specified by the user.
        The syntax for the rotor order is a list of the form ['I', 'II', 'III'], where 'I' is the left rotor, 'II' is the middle rotor, and 'III' is the right rotor. 
        '''
        # Now define the components.
        self.r_rotor = Rotor(order[2], self.key[2])
        self.m_rotor = Rotor(order[1], self.key[1], self.r_rotor)
        self.l_rotor = Rotor(order[0], self.key[0], self.m_rotor)
        # Define prev_rotor information for middle and right rotors.
        self.m_rotor.prev_rotor = self.l_rotor
        self.r_rotor.prev_rotor = self.m_rotor

    def set_plugs(self, swaps, replace=False):
        '''
        Update the plugboard settings. Swaps takes the form ['AB', 'CD'].

        If replace is true, then this method will erase the current plugboard settings and replace them with new ones. 
        '''
        self.plugboard.update_swaps(swaps, replace)
       # print('Plugboard successfully updated. New swaps are:')
       # for s in self.plugboard.swaps:
       #     print(s)       
