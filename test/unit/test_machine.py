import pytest
from machine import Enigma


@pytest.fixture
def enigma():
    return Enigma()

def test_validate_encoding(enigma):
    # Given an Enigma I with initial rotor position M, E, EU
    enigma.set_rotor_position("MEU")
    # When the machine is used encipher a sequence of 5 A's
    msg = enigma.encipher("AAAAA")
    # Then validate the ciphertext matches validated output
    assert msg == "GDXTZ"

def test_doublestep(enigma):
    # Test case taken from doublestep sample on source page
    # Reference: http://users.telenet.be/d.rijmenants/en/enigmatech.htm

    # Given an Enigma I with specified rotor order
    enigma.set_rotor_order(["III", "II", "I"])
    # And initial window position configured to rotate in subsequent steps
    enigma.set_rotor_position("KDO")

    # When the machine is used to encipher a message of length 6
    msg = enigma.encipher("AAAAAA")
    # Then the midrotor should doublestep resulting in final window positions
    # Sequence: KDO->KDP->KDQ->KER->LFS->LFT->LFU
    assert enigma.l_rotor.window == "L"
    assert enigma.m_rotor.window == "F"
    assert enigma.r_rotor.window == "U"

