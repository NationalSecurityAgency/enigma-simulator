'''
Known-answer tests for the Enigma simulator.

Expected values are for the Enigma I (Wehrmacht), reflector UKW-B, ring settings AAA.
They were cross-checked against an independent implementation (the py-enigma package,
EnigmaMachine.from_key_sheet(..., reflector='B', ring_settings=[0, 0, 0])), and the
first two also appear in published references:
  - AAAAA at AAA -> BDZGO is the common sanity check for rotors I-II-III.
  - The double-step sequences are from users.telenet.be/d.rijmenants/en/enigmatech.htm
    and https://en.wikipedia.org/wiki/Enigma_rotor_details#Normal_sequence
The double-step and stepping-direction tests follow upstream PR #6 by Zanion.
'''
import pytest

from machine import Enigma


def windows(e):
    return e.l_rotor.window + e.m_rotor.window + e.r_rotor.window


def make(order, position, swaps=None):
    e = Enigma(position, swaps, order)
    e.set_rotor_position(position)
    return e


@pytest.mark.parametrize('order, position, swaps, plaintext, ciphertext', [
    (['I', 'II', 'III'], 'AAA', None, 'AAAAA', 'BDZGO'),
    (['I', 'II', 'III'], 'MEU', None, 'AAAAA', 'GDXTZ'),
    (['I', 'II', 'III'], 'ADU', None, 'AAA', 'EQI'),
    (['III', 'II', 'I'], 'KDO', None, 'AAAAAA', 'ULMHJC'),
    (['V', 'III', 'I'], 'QEV', [('A', 'B'), ('C', 'D'), ('E', 'F')], 'HELLOWORLD', 'JXVXRUNEHE'),
    (['II', 'I', 'III'], 'YAQ', [('J', 'S'), ('H', 'Y'), ('N', 'F')],
     'THEWAYTOMAKEPEOPLETRUSTWORTHYISTOTRUSTTHEM',
     'WXCUVLBUCQTOXFMMITEBXLSCRXRXDTHDBKMKTKYMAW'),
])
def test_known_answers(order, position, swaps, plaintext, ciphertext):
    assert make(order, position, swaps).encipher(plaintext) == ciphertext


def test_reciprocal():
    ciphertext = make(['II', 'I', 'III'], 'TDS', [('J', 'S')]).encipher('ATTACKATDAWN')
    assert make(['II', 'I', 'III'], 'TDS', [('J', 'S')]).decipher(ciphertext) == 'ATTACKATDAWN'


def test_no_letter_encrypts_to_itself():
    e = make(['I', 'II', 'III'], 'AAA')
    assert all(c != 'A' for c in e.encipher('A' * 500))


def test_right_rotor_is_the_fast_rotor():
    e = make(['I', 'II', 'III'], 'AAA')
    e.encipher('AAAAA')
    assert windows(e) == 'AAF'


@pytest.mark.parametrize('order, position, expected', [
    # Rotors I-II-III: II (middle) has its notch at E, III (right) at V.
    (['I', 'II', 'III'], 'ADU', ['ADV', 'AEW', 'BFX', 'BFY']),
    # Rotors III-II-I: I (right) has its notch at Q.
    (['III', 'II', 'I'], 'KDO', ['KDP', 'KDQ', 'KER', 'LFS', 'LFT', 'LFU']),
])
def test_double_step(order, position, expected):
    e = make(order, position)
    seen = []
    for _ in expected:
        e.encipher('A')
        seen.append(windows(e))
    assert seen == expected


def test_period():
    # With the double step the three-rotor period is 26 * 25 * 26 = 16,900, not 26 ** 3.
    e = make(['I', 'II', 'III'], 'AAA')
    for _ in range(26 * 25 * 26):
        e.step_rotors()
    assert windows(e) == 'AAA'


def test_long_message_matches_reference():
    # 700 key presses cover several middle-rotor turnovers and a double step.
    ciphertext = make(['I', 'II', 'III'], 'AAA').encipher('A' * 700)
    assert ciphertext.startswith('BDZGOWCXLTKSBTMCDLPB')
    assert ciphertext.endswith('PWITKGVIBOOMTNDUHQPH')
