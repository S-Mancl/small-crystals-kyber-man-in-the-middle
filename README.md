# CRYSTALS-Kyber & Man in the Middle

This is my project for the Cryptography teaching at [SSRI (computer systems and networks security)](https://www.unimi.it/en/education/computer-systems-and-networks-security) at [Università Statale degli Studi di Milano, Italy](https://www.unimi.it/en).

Questo è il progetto per il corso di Crittografia a Sicurezza dei Sistemi e delle Reti Informatiche all'Università Statale di Milano.

## What is this?

### An implementation of CRYSTALS-Kyber
This is an implementation of a (reduced) version of the [Kyber Key Encapsulation Mechanism](https://en.wikipedia.org/wiki/Kyber), winner of the NIST competition for Post-Quantum Cryptography Standards.

It simulates a scenario where two players want to use AES but need to agree on common keys.

![Kyber Key Encapsulation Mechanism](https://github.com/S-Mancl/small-crystals-kyber-man-in-the-middle/blob/main/images/kem.png)

### A demonstration of Man in the Middle attacks against the basic KEM protocol
It also demonstrates how the basic Kyber.KEM protocol can be vulnerable to a Man in the Middle attack.

The screenshot below shows two things that are possible in this scenario:
1. to understand the content of secrets messages
2. to edit those messages

![Demonstration of Man in the Middle](https://github.com/S-Mancl/small-crystals-kyber-man-in-the-middle/blob/main/images/man-in-the-middle.png)

## Where to learn more about it?

You can look at the slideshow under `./slideshow`. It also has a bibliography section with the papers and articles that inspired this work.

## How to try it?

**Prerequisites:** you need to have docker installed.

**Build and exec:**

```bash
git clone https://github.com/S-Mancl/small-crystals-kyber-man-in-the-middle
cd small-crystals-kyber-man-in-the-middle/code
make build
make up
```

After the terminals open on the three nodes you can start the clients (on `Alderaan` and `Tatooine`) with

```bash
python3 lightknife_client.py
```

And the server (on `Deathstar`) with:

```bash
python3 lightknife_server.py [--evil]
```

Use `--evil` if you want to intercept the messages and change them.

**Commands:**
- `vim` like bindings: `:q`,`:quit` are available in command mode
- in command mode type `i` to enter insert mode, write your message then enter to send it
- in command mode use `:connect` to perform the key encapsulation protocol
- in command mode use `:r` to reload the list of messages with eventual new ones.

**Close:**

```bash
make down
make clean
```


