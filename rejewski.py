#! /usr/bin/python
"""
Module containing code to recreate Rejewski's attack on Enigma.

When you get stuck, Https://en.wikipedia.org/wiki/Grill_(cryptology) has a lot of helpful information on how this attack should progress.
"""
# Import helpful tools
from tqdm import tqdm
from itertools import permutations, product, chain
import pickle
import random as r

# Import enigma stuff
import machine

# Messages for encryption with message key TDJTDJ
msg1 = 'A calm and modest life brings more happiness than the pursuit of success combined with constant restlessness Albert Einstein'
msg2 = 'The way to make people trustworthy is to trust them Ernest Hemmingway'
msg3 = 'The future belongs to those who believe in the beauty of their dreams Eleanor Roosevelt'
'''
Outline for how they will solve this so I don't forget.

- We set a secret day key, rotor order, and permutations. DONE
- We choose a bunch of random message keys and generate the six-letter encryption. DONE
- We ask them to recreate the alphabet mappings for the AD, BE, CF pairs.
  - They will use the message key encryptions to this.
  - Do we want them to do this by hand or should we provide them with a function?
- They generate chains from the alphabet mappings.
  - Again, we can provide them with a method to do this if we want or they can do it by hand.
- They use their generated chains to index our provided dictionary. We will specify the format they need to use to index the dictionary (probably a string like 'AD:5431 BD:621 CF:8341').
- Then, they use the rotor settings they recovered to guess the plugboard (not yet sure how to do this).

*NOTE* I think the best method might be to write a Jupyter notebook containing all the functionality you would need to programmatically start with a secret key and message encrypts (given that you will have the dictionary of key encryption) and then systematically remove parts until you think it will be feasible for them.

'''
############################## CODE TO GENERATE CHAIN DICTIONARY ##############################

def make_chain_length_dict():
    '''
    Function to create the chains dictionary for all possible key/rotor combinations for Enigma.
    '''
    # Define some variables (for now)
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    keys = product(alphabet, repeat=3) # Get the Cartesian product of 3 alphabets
    enigma = machine.Enigma() # Create an enigma machine.
    # For possible day key in the set of all day keys
    chains_dict = {}
    for key in tqdm(keys):
        # For rotor combination in rotors.
        for order in permutations(['I', 'II', 'III']):
            AD = {letter:None for letter in alphabet}
            BE = {letter:None for letter in alphabet}
            CF = {letter:None for letter in alphabet}
            # While we haven't made full alphabets for AD, BE, CF perms for this day key and rotor combo.
            enigma.set_rotor_order(order)
            while any(AD[i] is None for i in AD) or any(BE[i] is None for i in BE) or any(CF[i] is None for i in CF):
                # Reset the day key.
                enigma.set_rotor_position(key[0] + key[1] + key[2])
                # Encrypt the message key twice.
                m_key = alphabet[r.randint(0,25)] + alphabet[r.randint(0,25)] + alphabet[r.randint(0,25)]
                cipher = enigma.encipher(m_key + m_key)
                # Take the cipher text and add it to the alphabet set for day key.
                AD[cipher[0]] = cipher[3] if AD[cipher[0]] is None else AD[cipher[0]]
                BE[cipher[1]] = cipher[4] if BE[cipher[1]] is None else BE[cipher[1]]
                CF[cipher[2]] = cipher[5] if CF[cipher[2]] is None else CF[cipher[2]]
            # Now make the chains from the dictionaries and generate dictionary index.
            index = generate_chain_index(make_chains_from_permutation_dict([AD,BE,CF]))
            # Deal with the case that you have multiple mappings to the same key pair.
            if index not in chains_dict:
                chains_dict[index] = [(key, order)]
            else:
                chains_dict[index].append((key,order))
    pickle.dump(chains_dict, open('./chains.pickle', 'wb'), protocol=2)
    return chains_dict

def generate_permutation_dicts(message_encrypts):
    ''' Outputs AD, BE, and CF
    dictionaries generated from a series of double message key encryptions.

    Params: message_encrypts = an iterator/list containing a double message key encryptions.
    '''
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    AD = {letter:None for letter in alphabet}
    BE = {letter:None for letter in alphabet}
    CF = {letter:None for letter in alphabet}
    for m in message_encrypts:
         if any(AD[i] is None for i in AD) or any(BE[i] is None for i in BE) or any(CF[i] is None for i in CF):
                AD[m[0]] = m[3] if AD[m[0]] is None else AD[m[0]]
                BE[m[1]] = m[4] if BE[m[1]] is None else BE[m[1]]
                CF[m[2]] = m[5] if CF[m[2]] is None else CF[m[2]]
    return AD, BE, CF

def make_chains_from_permutation_dict(permutation_dicts):
    '''
    TASK: given a dictionary linking the first and fourth (or second and fifth or third and sixth) letter combinations from the message keys, generate the length of chains (i.e. cycles of letters) found in the dictionary.

    '''
    chain_list = []
    for perm_dict in permutation_dicts:
        alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        chains = []
        while len(alphabet) > 0:
            next_chain = perm_dict[alphabet[0]]
            next_letter = perm_dict[next_chain[0]]
            # must remove the first two letters in the chain.
            alphabet = alphabet.replace(alphabet[0], '')
            alphabet = alphabet.replace(next_chain, '')
            while next_letter != next_chain[0]:
                next_chain += next_letter
                alphabet = alphabet.replace(next_letter, '')
                next_letter = perm_dict[next_letter]
            chains.append(next_chain)
            alphabet.replace(next_letter, '')
        chain_list.append(chains)
    return chain_list

def generate_chain_index(chains):
    '''
    Given a list of chains for the AD, BE, and CF pairs, find their lengths and put them in a digestable form for indexing.

    MAJOR ASSUMPTION: these chains will come directly from my code, so they will be in the order AD, BE, CF.
    '''
    chain_index = 'AD:'
    for i, chain_list in enumerate(chains):
        if i is 1:
            chain_index = chain_index + ' BE:'
        elif i is 2:
            chain_index = chain_index + ' CF:'
        # Sort the chains to make sure the number is unique.
        chain_list.sort(key=lambda x: len(x))
        for c in chain_list:
            chain_index = chain_index + str(len(c))
    return chain_index

############################## CODE TO GENERATE MESSAGES FROM DAY KEY ##############################

# Set the Enigma secrets.
SECRET_DAY_KEY = 'YAQ'
SECRET_ROTOR_ORDER = ['II', 'I', 'III']
SECRET_SWAPS = [('J', 'S'), ('H', 'Y'), ('N', 'F')]

def make_messages(day_key, swaps, rotor_order, msg_key_count, pickleIt=False):
    '''
    Given the secret settings for the Enigma machine, generate a bunch of message keys and save them off.
    '''
    message_key_encrypts = []
    abt = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    enigma = machine.Enigma(day_key, swaps, rotor_order)
    for i in range(msg_key_count):
        msg_key = abt[r.randint(0, len(abt)-1)] + abt[r.randint(0, len(abt)-1)] + abt[r.randint(0, len(abt)-1)]
        # Reset the day key.
        enigma.set_rotor_position(day_key)
        message_key_encrypts.append(enigma.encipher(msg_key + msg_key))
    if pickleIt:
        pickle.dump(message_key_encrypts, open('./message_key_encrypts.pickle', 'wb'), protocol=2)
    return message_key_encrypts

def test_chains(day_key, rotor_order):
    '''
    Given a day key and rotor order, test to make sure the same thing exists in the chain dictionary generated above. 
    '''
    AD, BE, CF = generate_permutation_dicts(make_messages(day_key, None, rotor_order, 200))
    index = generate_chain_index(make_chains_from_permutation_dict([AD,BE,CF]))
    print('Day key ' + day_key + ' with rotor order ' + str(rotor_order) + ' generates index ' + index)
    return index
                                     
                                            
