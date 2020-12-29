# HV20.16 Naughty Rudolph

| <!-- --> | <!-- --> |
| --- | --- |
| **Author**     | dr_nick |
| **Level**      | hard |
| **Categories** | `programmig`, `fun` (oh no!) |

## Description

Santa loves to keep his personal secrets on a little toy cube he got from a kid called Bread (:bread:). Turns out that was not a very good idea. Last night Rudolph got hold of it and frubl'd it about five times before spitting it out. Look at it! All the colors have come off! Naughty Rudolph!

[Download](./804fa458-c10c-4627-89df-18028bff6efa.stl)

### Hints
- The flag matches `/^HV20{[a-z3-7_@]+}$/` and is read face by face, from left to right, top to bottom
- The cube has been scrambled with ~5 moves in total
- jElf has already started trying to solve the problem, however he got lost with all the numbers. Feel free to use his [current state](./28a1f355-6be2-458f-b24e-e0a8f8c60664.java) if you don't want to start from scratch...

## Approach

The steps to solving this challenge can be summarised as follows:
- Find out what an STL file is https://en.wikipedia.org/wiki/STL_%28file_format%29.
- Check out the STL file at https://www.viewstl.com/.
- Learn Rubiks Cube notation: https://ruwix.com/the-rubiks-cube/notation/ and https://ruwix.com/the-rubiks-cube/notation/advanced/
- Common Rubik solvers don't help much, since they ignore the orientation of tiles.
- Write a custom solver algorithm (see below) that mainly checks the orientation (inspired by https://pypi.org/project/rubik-cube/).
- Extend https://pypi.org/project/rubik-cube/ to apply double-moves (like `L2`, `B2` etc.), since these seem to be needed by the challenge.
- Parallelize processing to be more efficicient.


The custom solver, instead of computing new orientations, used a translation table producing a state by applying a given transition to a given cube state. A state is defined by the set of orientations of all tiles on a cube.

A cube is represented as follows, where `F` is front, `U` is upper side, `D` is downside, `L` is left side, `R` is right side and `B` is back side.
```
  +-+
  |U|
+-+-+-+-+
|L|F|R|B|
+-+-+-+-+
  |D|
  +-+
```
The approach is to go through all combinations including 5 moves as defined by the World Cube Association (WCA) including moves `F`, `U`, `R`, `B`, `L`, `D` as well as their inverses (e.g. `F'` and double moves `F2`).

A solution is reached whenever all faces are aligned (or, as in my case, a majority of them, if the transition table is buggy).

As soon as a solution was found, we can also compute the cube holding the characters, which is more expensive, hence delayed.

Here's the solver's output:
```bash
$ time python solver.py 
18 possible different moves. 5 moves in total. 1889568 possible sequences.
///////// PROGRESS: 100000 //////////
///////// PROGRESS: 200000 //////////
///////// PROGRESS: 300000 //////////
///////// PROGRESS: 400000 //////////
///////// PROGRESS: 500000 //////////
///////// PROGRESS: 600000 //////////
///////// PROGRESS: 700000 //////////
###################
# Move: Bi Ui R Di F2
------------------
6ceisrhhoHV25o_}tsipl0{ndt@al_n_eo_sa__7a_cs34se_klew_
    6ce
    isr
    hho
HV2 5o_ }ts ipl
0{n dt@ al_ n_e
o_s a__ 7a_ cs3
    4se
    _kl
    ew_
    👈👈👈
    👈👈👈
    👈👈👈
👆👆👆 👈👈👈 👇👇👇 👉👉👉
👆👆👆 👈👈👈 👇👇👇 👉👉👉
👆👆👆 👈👈👈 👇👇👇 👉👉👉
    👈👈👈
    👈👈👈
    👈👈👈
///////// PROGRESS: 800000 //////////
///////// PROGRESS: 900000 //////////
///////// PROGRESS: 1000000 //////////
///////// PROGRESS: 1100000 //////////
///////// PROGRESS: 1200000 //////////
///////// PROGRESS: 1300000 //////////
///////// PROGRESS: 1400000 //////////
///////// PROGRESS: 1500000 //////////
///////// PROGRESS: 1600000 //////////
///////// PROGRESS: 1700000 //////////
///////// PROGRESS: 1800000 //////////

THE END.

real    1m41.343s
user    7m50.505s
sys 0m27.729s

```

Finally, read out the cube side by side (aligned and rotated to point upwards) to find the following parts of the final flag:

- L: `HV20{no_s`
- B: `le3p_sinc`
- D: `e_4wks_le`
- F: `ad5_to_@_`
- U: `hi6hscore`
- R: `_a7_last}`

And assemble these strings to a flag:

`HV20{no_s` + `le3p_sinc` + `e_4wks_le` + `ad5_to_@_` + `hi6hscore` + `_a7_last}`

Checkout the solver [here](./dec16.tar.bz2)

## Flag
`HV20{no_sle3p_since_4wks_lead5_to_@_hi6hscore_a7_last}`

## Notes to self
- Don't do bugs.
- think first, then implement.
