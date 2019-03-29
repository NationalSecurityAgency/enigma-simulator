#!/usr/bin/python

'''
Enigma Machine Simulation
Author: Emily Willson
Date: April 6, 2018

Details: This file holds the components of the Engima machine. The machine.py file contains the code that will actually run the machine.
'''

# Define global variables to hold rotor wiring and stepping information.
# Wiring information is derived from users.telnet.be/d.rijmenants/en/engimatech.htm#wiringtables.

ROTOR_WIRINGS = {
    'I': {'forward':'EKMFLGDQVZNTOWYHXUSPAIBRCJ',
          'backward':'UWYGADFPVZBECKMTHXSLRINQOJ'},
    'II':{'forward':'AJDKSIRUXBLHWTMCQGZNPYFVOE',
          'backward':'AJPCZWRLFBDKOTYUQGENHXMIVS'},
    'III':{'forward':'BDFHJLCPRTXVZNYEIWGAKMUSQO',
           'backward':'TAGBPCSDQEUFVNZHYIXJWLRKOM'},
    'V':{'forward':'VZBRGITYUPSDNHLXAMJQOFECK',
           'backward':'QCYLXWENFTZOSMVJUDKGIARPHB'}
}

# The next left rotor will step when the specified letters are visible in the window for that rotor.
ROTOR_NOTCHES = {
    'I':'Q', # Next rotor steps when I moves from Q -> R
    'II':'E', # Next rotor steps when II moves from E -> F
    'III':'V', # Next rotor steps when III moves from V -> W
    'V':'Z' # Next rotor steps when V moves from Z -> A
    }

# Define alphabet global variable in order to do proper index matching between rotors.
ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

class Rotor:
    '''
    This class defines the rotors for the Engima machine.
    '''
    def __init__(self, rotor_num, window_letter, next_rotor=None, prev_rotor=None):
        if rotor_num == 'I' or rotor_num == 'II' or rotor_num == 'III' or rotor_num == 'V':
            self.rotor_num = rotor_num
            self.wiring = ROTOR_WIRINGS[rotor_num]
            self.notch = ROTOR_NOTCHES[rotor_num]
            # This is the letter visible to the operator.
            # Defining this is akin to defining the initial setting of the machine.
            self.window = window_letter.upper()
            self.offset = ALPHABET.index(self.window)
            self.next_rotor = next_rotor
            self.prev_rotor = prev_rotor
        else:
            print('Please select I, II, III, or V for your rotor number and provide the initial window setting (i.e. the letter on the wheel initially visible to the operator.')
            return None

    def __repr__(self):
        print('Wiring: ')
        print(self.wiring)
        return 'Window: ' + self.window

    def step(self):
        """
        Steps the rotor.
        If a next rotor is specified, do the check to see if we've reached the notch,
        thus requiring that rotor to step.
        """
        if self.next_rotor and self.window==self.notch:
            self.next_rotor.step()
        self.offset = (self.offset + 1)%26
        self.window = ALPHABET[self.offset]
       # print(self.offset, self.window)

    def encode_letter(self, index, forward=True, return_letter=False, printit=False):
        """
        Takes in an index associated with an alphabetic character.
        Uses internal rotor wiring to determine the output letter and its index.

        NOTE: indexing here is done with respect to the window position of the rotor.
        The letter visible in the window is the 0th letter in the index.
        The index then increments up the alphabet from this letter.

        EXAMPLE: 'Z' in window, then Z=0, A=1, B=2, etc.  Input and output
        letters from a rotor follow the same indexing scheme.
        """
        # Make sure it's number and not a letter.
        if type(index)==str and len(index) == 1:
            index = ALPHABET.index(index.upper())
        if forward:
            key = 'forward'
        else:
            key = 'backward'
        # Check the wiring table and find the associated letter with this index.
        output_letter = self.wiring[key][(index + self.offset)%26]
        # Determine output index associated with this letter based on wiring.
        output_index = (ALPHABET.index(output_letter) - self.offset)%26
        if printit:
            print('Rotor ' + self.rotor_num + ': input = ' +
                  ALPHABET[(self.offset + index)%26] + ', output = ' + output_letter)
        if self.next_rotor and forward:
            return self.next_rotor.encode_letter(output_index, forward)
        elif self.prev_rotor and not forward:
            return self.prev_rotor.encode_letter(output_index, forward)
        else:
            if return_letter:
                return ALPHABET[output_index]
            else:
                return output_index

    def change_setting(self, new_window_letter):
        '''
        Allows the operator to define a new setting for this rotor.
        This changes the window letter therefore changing the setup of the rotor.
        '''
        self.window = new_window_letter.upper()
        self.offset = ALPHABET.index(self.window)

class Reflector:
    '''
    This class defines the reflector for the Engima machine.
    '''
    def __init__(self):
        # Note: this is the wiring for Reflector B of the Wehrmaht Engima.
        self.wiring = {'A':'Y', 'B':'R', 'C':'U', 'D':'H', 'E':'Q', 'F':'S', 'G':'L', 'H':'D',
                       'I':'P', 'J':'X', 'K':'N', 'L':'G', 'M':'O', 'N':'K', 'O':'M', 'P':'I',
                       'Q':'E', 'R':'B', 'S':'F', 'T':'Z', 'U': 'C', 'V':'W', 'W':'V', 'X':'J',
                       'Y':'A', 'Z':'T'
                      }
    def __repr__(self):
        print('Reflector wiring: ')
        print(self.wiring)
        return ''

class Plugboard():
    '''
    This class defines the plugboard for the Engima machine.
    '''
    def __init__(self, swaps):
        '''
        Initialize the plugboard swaps.
        Input swaps should be of the form: ['AB', 'XR')] if A,B and X,R are swaps.
        '''
        self.swaps = {}
        if swaps != None and len(swaps) > 0:
            for swap in swaps:
                self.swaps[swap[0]] = swap[1]
                self.swaps[swap[1]] = swap[0]

    def __repr__(self):
        print('Swaps:')
        print(self.swaps)
        return ''

    def print_swaps(self):
        '''
        Prints a nice representation of swaps so the user can view the internal workings.
        '''
        pass

    def update_swaps(self, new_swaps, replace=False):
        '''
        Takes in new swap settings.
        If replace==True, will replace all plugboard settings with new settings.
        If replace==False, will leave current settings in place but update with new settings.
        '''
        if replace:
            self.swaps = {}
        if new_swaps != None and isinstance(new_swaps, list):
            if len(new_swaps) > 6:
                print('Only a maximum of 6 swaps is allowed.')
            else:
                for swap in new_swaps:
                    self.swaps[swap[0]] = swap[1]
                    self.swaps[swap[1]] = swap[0]
        return
