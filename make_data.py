#!/usr/bin/env python3
'''
Generate the data files that BreakingEnigma.ipynb and MasterEnigmaCracker.ipynb load:

  chains.pickle                 the cycle-length catalog: index string -> [(day key, rotor order), ...]
  message_key_encrypts.pickle   doubly enciphered message keys sent under the secret day key
  encrypt1.txt .. encrypt3.txt  messages enciphered under the first message key

The secret day key, rotor order, plugboard and plaintexts come from rejewski.py. The output is
deterministic: running this again produces byte-identical files.

Usage:
  python make_data.py           build any file that is missing
  python make_data.py --force   rebuild all of them

The catalog covers all 6 rotor orders x 17,576 day keys (105,456 settings). Each setting is
enciphered once per plaintext letter rather than with random message keys until the permutations
fill up, so the build takes about a minute on one core.
'''
import argparse
import os
import pickle
import random
import time
from itertools import permutations, product

import machine
import rejewski

ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
ROTORS = ['I', 'II', 'III']
# First message key (see the note at the top of rejewski.py). Its encipherment, ZEUATW, is the first
# entry of message_key_encrypts.pickle, and encrypt1-3.txt are sent under it.
FIRST_MESSAGE_KEY = 'TDJ'
MESSAGE_KEY_COUNT = 500
SEED = 1932
MESSAGE_FILES = ['encrypt1.txt', 'encrypt2.txt', 'encrypt3.txt']


def chain_index(enigma, day_key):
    '''
    Cycle-length index of the AD, BE and CF permutations for one day key (no plugboard).

    For every plaintext letter p, the ciphertext of pppppp at the day key gives one pair for each
    permutation (letter 1 -> letter 4, 2 -> 5, 3 -> 6). Running all 26 letters gives the complete
    permutations, so no random sampling is needed.
    '''
    perms = [{}, {}, {}]
    for p in ALPHABET:
        enigma.set_rotor_position(day_key)
        c = enigma.encipher(p * 6)
        for i in range(3):
            perms[i][c[i]] = c[i + 3]
    return rejewski.generate_chain_index(rejewski.make_chains_from_permutation_dict(perms))


def make_catalog():
    orders = list(permutations(ROTORS))
    enigma = machine.Enigma()
    catalog = {}
    start = time.time()
    for n, first in enumerate(ALPHABET, 1):
        for rest in product(ALPHABET, repeat=2):
            key = (first,) + rest
            for order in orders:
                enigma.set_rotor_order(list(order))
                index = chain_index(enigma, ''.join(key))
                catalog.setdefault(index, []).append((key, order))
        print('  catalog: day keys %sAA-%sZZ done (%d/26, %.0f s)' % (first, first, n, time.time() - start),
              flush=True)
    return catalog


def make_message_key_encrypts():
    rng = random.Random(SEED)
    keys = [FIRST_MESSAGE_KEY] + [''.join(rng.choice(ALPHABET) for _ in range(3))
                                  for _ in range(MESSAGE_KEY_COUNT - 1)]
    enigma = machine.Enigma(rejewski.SECRET_DAY_KEY, rejewski.SECRET_SWAPS, rejewski.SECRET_ROTOR_ORDER)
    encrypts = []
    for key in keys:
        enigma.set_rotor_position(rejewski.SECRET_DAY_KEY)
        encrypts.append(enigma.encipher(key + key))
    return encrypts


def make_messages():
    enigma = machine.Enigma(FIRST_MESSAGE_KEY, rejewski.SECRET_SWAPS, rejewski.SECRET_ROTOR_ORDER)
    out = []
    for msg in (rejewski.msg1, rejewski.msg2, rejewski.msg3):
        enigma.set_rotor_position(FIRST_MESSAGE_KEY)
        out.append(enigma.encipher(msg))
    return out


def write(path, data):
    with open(path, 'wb') as f:
        f.write(data)
    print('wrote %s (%d bytes)' % (path, len(data)))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--force', action='store_true', help='rebuild files that already exist')
    args = parser.parse_args()
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    def wanted(path):
        if os.path.exists(path) and not args.force:
            print('%s exists, skipping (use --force to rebuild)' % path)
            return False
        return True

    if wanted('chains.pickle'):
        print('Building the cycle-length catalog (about a minute)...', flush=True)
        write('chains.pickle', pickle.dumps(make_catalog(), protocol=2))
    if wanted('message_key_encrypts.pickle'):
        write('message_key_encrypts.pickle', pickle.dumps(make_message_key_encrypts(), protocol=2))
    for path, text in zip(MESSAGE_FILES, make_messages()):
        if wanted(path):
            write(path, text.encode('ascii'))


if __name__ == '__main__':
    main()
