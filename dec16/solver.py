import itertools
import multiprocessing
from typing import List

from cube import Cube
from oriented_cube import O_DOWN as D
from oriented_cube import O_LEFT as L
from oriented_cube import O_RIGHT as R
from oriented_cube import O_UP as U
from oriented_cube import OrientedCube

possible_moves = ["B2", "F2", "D2", "U2", "R2", "L2", "Bi", "B", "Fi", "F", "Di", "D", "Ui", "U", "Ri", "R", "Li",
                  "L", ]



# Look at the cube via https://www.viewstl.com/
def main():
    print("%s possible different moves. 5 moves in total. %s possible sequences." % (len(possible_moves), len(possible_moves)**5))

    with multiprocessing.Pool(6) as pool:
        i = 0
        seq_gen = generate_sequences()
        seqs = list(itertools.islice(seq_gen,50))
        while seqs != None and len(seqs) > 0:
            i += 50
            if i % 100_000 == 0:
                print("///////// PROGRESS: %s //////////" % i)

            pool.map(calc, seqs)
            seqs = list(itertools.islice(seq_gen, 50))

        print()
        print("THE END.")
        # Expected solving moves: Bi Ui R Di F2

def calc(sequence):
    oriented = OrientedCube([
                    U, L, L,
                    D, U, U,
                    U, U, R,
           L, R, L, R, R, U, U, R, L, R, R, R,
           L, U, U, R, R, L, R, R, L, L, D, R,
           R, R, R, U, U, R, R, R, L, L, D, R,
                    U, U, R,
                    U, U, R,
                    U, L, U
    ])
    oriented.sequence(sequence)
    if oriented.is_solved():
        print("###################")
        print("# Move: %s" % sequence)
        print("------------------")
        cube = Cube(""
                    "    lo_"
                    "    ssc"
                    "    in2"
                    "6_e s_5 hp} ohH"
                    "i{a @tr tll a_V"
                    "es3 o_4 sn_ _e7"
                    "    e_a"
                    "    wkd"
                    "    _0c")
        cube.sequence(sequence)
        print(cube.flat_str())
        print(cube)
        print(oriented)


def generate_sequences() -> List[str]:
    for i in possible_moves:
        for j in possible_moves:
            for k in possible_moves:
                for l in possible_moves:
                    for m in possible_moves:
                            yield "%s %s %s %s %s" % (i, j, k, l, m)


if __name__ == '__main__':
    main()
