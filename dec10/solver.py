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
# print(clique.graph_number_of_cliques(g))
kids=[104,118,55,51,123,110,111,116,95,84,72,69,126,70,76,65,71,33,61,40,124,115,48,60,62,83,79,42,82,121,125,45,98,114,101,97,100]
# print(len(set(kids)))
matching_cliques=0


# for kid in kids: 
#     print("#### KID: %s" % kid)
#     cliques = clique.cliques_containing_node(g , kid)
#     friends = 0
#     largest_clique = 0
#     for clicke in cliques:
#         clique_size = len(clicke)
#         largest_clique = clique_size if clique_size > largest_clique else largest_clique
#         friends += clique_size
#         # for c in clicke:
#         #     print(chr(c), end='')
#         # print()
#     print("///// Kid %s has %d friends."%(kid, friends))
#     print("///// Kid's %s largest clique is %d (%s) friends."%(kid, largest_clique, chr(largest_clique)))

cliques_per_kid = {}

for clique in cliques:
    # print(str(len(set(kids).intersection(set(list(clique))))) + ": ", end='')
    # print(clique)
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

for kid in kids:
    clickes = cliques_per_kid[kid]
    # print("#### KID %s has %d clickes" % (kid, len(clickes))
    largest_clique = 0
    for clique in clickes:
        clique_size = len(clique)
        largest_clique = clique_size if clique_size > largest_clique else largest_clique
        # for c in clique:
        #     print(chr(c), end='')
        # print("\n========")
    print(chr(largest_clique), end='')
    # print("Kid %s' largest clique is %d (%s)" % (kid, largest_clique, chr(largest_clique)))

# print("Matching cliques: %s" % matching_cliques)
print()
