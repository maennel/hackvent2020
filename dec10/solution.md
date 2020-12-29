# HV20.10 Be patient with the adjacent

| <!-- --> | <!-- --> |
| --- | --- |
| **Author**     | Bread |
| **Level**      | medium |
| **Categories** | `programming` |


## Description

Ever wondered how Santa delivers presents, and knows which groups of friends should be provided with the best gifts? It should be as great or as large as possible! Well, here is one way.

Hmm, I cannot seem to read the file either, maybe the internet knows?

[Download](./7b24b79f-d898-4480-bc1b-e09742f704f7.col.b)

### Hints
- Hope this cliques for you
- `bin2asc` will help you with this, but ...
- segfaults can be fixed - maybe read the source
- If you are using Windows for this challenge, make sure to add a `b` to to the `fopen` calls on lines 37 and 58
- There is more than one thing you can do with this type of file! Try other options...
- Groups, not group

## Approach

The given `.col.b` file has the following header:
```
284
c -------------------------------- 
c Reminder for Santa:
c   104 118 55 51 123 110 111 116 95 84 72 69 126 70 76 65 71 33 61 40 124 115 48 60 62 83 79 42 82 121 125 45 98 114 101 97 100 are the nicest kids.
c   - bread.
c -------------------------------- 
p edges 18876 439050
```

Interpreting the decimal numbers directly and converting them to binary produced the string `hv73{not_THE~FLAG!=(|s0<>SO*Ry}-bread`. Another "flake" - doh!

As I had to find out first, `.col.b` files are used to store graphs in a binary [DIMACS](http://prolland.free.fr/works/research/dsat/dimacs.html) format. Their sibling is `.col` which is the same but in an ASCII format.

To convert between the two formats, the program `bin2asc` (found [here](https://mat.gsia.cmu.edu/COLOR/format/binformat.shar) or [here](http://archive.dimacs.rutgers.edu/pub/challenge/graph/translators/binformat/NotANSI/)) had to be compiled.

However, `bin2asc` crashed... As we had 18876 vertices and 439050 edges, the problem apparently was that the max number of allowed vertices (5000) was lower than the number of edges in our source file. So, the limit had to be raised in the file `genbin.h`.

Next, we apparently had to form [cliques](https://en.wikipedia.org/wiki/Clique_(graph_theory)) in our graph.

This was done using the python library `networkx` (see https://networkx.org/documentation/stable/reference/algorithms/clique.html).

Long story short, for each of the nice kids, we had to find the size of the largest clique they belong to, convert that size into a character, which then formed the flag.

```python
#!/usr/bin/env python

import networkx as nx
from networkx.algorithms import clique

g = nx.Graph()
with open("./7b24b79f-d898-4480-bc1b-e09742f704f7_mod.col", "r") as f:
    for l in f:
        if l[0] == 'e':
            _, a, b = l.split(' ', 2)
            g.add_edge(int(a), int(b))

cliques = clique.find_cliques(g)
kids=[104,118,55,51,123,110,111,116,95,84,72,69,126,70,76,65,71,33,61,40,124,115,48,60,62,83,79,42,82,121,125,45,98,114,101,97,100]
matching_cliques=0

cliques_per_kid = {}

# Find all cliques for each kid.
for clique in cliques:
    inters = set(kids).intersection(set(clique))
    if len(inters) > 0:
        for i in inters:
            if i not in cliques_per_kid:
                kid_cliques = list()
            else:
                kid_cliques = cliques_per_kid[i]
            if len(clique) > 2:
                kid_cliques.append(clique)
            cliques_per_kid[i] = kid_cliques

# For each kid, find the largest clique it belongs to.
for kid in kids:
    clickes = cliques_per_kid[kid]
    largest_clique = 0
    for clique in clickes:
        clique_size = len(clique)
        largest_clique = clique_size if clique_size > largest_clique else largest_clique
    print(chr(largest_clique), end='')
print()
```

## Flag
`HV20{Max1mal_Cl1qu3_Enum3r@t10n_Fun!}`

## Credits
Thanks to :bread: for keeping me on track, when I almost gave up - and for extending the deadline for flag submission ;).
