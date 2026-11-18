# enigma-simulator

This enigma-simulator project is an educational tool which simulates the
workings of an [Enigma machine][wiki-enigma], the Germans' main military
encryption tool during [World War II][wiki-ww2]. The software allows users to
encrypt and decrypt messages. Additionally, the simulation includes a
step-by-step guide that teaches users how to recover Enigma keys.

This project was created and maintained by the [National Security Agency][nsa].

## What the notebooks teach

`BreakingEnigma.ipynb` walks through Marian Rejewski's 1932 attack on the
Enigma message key. Each intercepted message begins with its three-letter
message key enciphered twice under the day key, so letters 1 and 4, 2 and 5,
and 3 and 6 are encryptions of the same letter. A day's traffic therefore
gives three permutations (AD, BE and CF) whose cycle lengths do not depend on
the plugboard. Looking those cycle lengths up in a catalog computed for every
rotor order and starting position narrows the day key to a few candidates,
which are tested by decrypting the messages and recovering the plugboard.
`MasterEnigmaCracker.ipynb` contains the solutions.

## Running the notebooks

The notebooks need Python 3 and a few data files that are generated locally
rather than stored in the repository:

```
pip install -r requirements.txt
python make_data.py
jupyter notebook BreakingEnigma.ipynb
```

`make_data.py` writes `chains.pickle` (the cycle-length catalog for all
6 x 26^3 rotor orders and day keys), `message_key_encrypts.pickle` and
`encrypt1.txt` to `encrypt3.txt`, using the secret settings in `rejewski.py`.
It takes about a minute, produces the same bytes on every run, and skips files
that already exist unless given `--force`.

## License

The simulator and notebooks were written at the National Security Agency
(original author Emily Willson). Portions created by the U.S. Government are
not subject to U.S. copyright; contributions are under the MIT License. See
[LICENSE](LICENSE).

[nsa]: https://www.nsa.gov
[wiki-enigma]: https://en.wikipedia.org/wiki/Enigma_machine
[wiki-ww2]: https://en.wikipedia.org/wiki/World_War_II
