#!/usr/bin/env python3
import string, functools
from graphviz import Digraph

class Signpost(object):
    def __init__(self, directions, names):
        self.size = len(directions)
        self.directions = directions
        self.names = names
        for i in range(len(self.names)):
            for j in range(len(self.names[i])):
                if self.names[i][j] == 0 or self.names[i][j] == '':
                    self.names[i][j] = str((i + 1, j + 1))
                else:
                    self.names[i][j] = str(self.names[i][j])
        self.all_names = set(functools.reduce(lambda x, y: x + y, self.names))
        self.edges = []
        for line_i in range(len(self.names)):
            dir_line, name_line = self.directions[line_i], self.names[line_i]
            for item_j in range(len(name_line)):
                print(line_i, item_j)
                direction, name = dir_line[item_j], name_line[item_j]
                print(direction, name)
                if direction == 'D':
                    for line_l in range(line_i + 1, len(self.names)):
                        self.edges.append((name, self.names[line_l][item_j]))
                elif direction == 'U':
                    for line_l in range(0, line_i):
                        self.edges.append((name, self.names[line_l][item_j]))
                elif direction == 'R':
                    for item_l in range(item_j + 1, len(name_line)):
                        self.edges.append((name, self.names[line_i][item_l]))
                elif direction == 'L':
                    for item_l in range(0, item_j):
                        self.edges.append((name, self.names[line_i][item_l]))
                elif direction == 'UR':
                    line_l, item_m = line_i, item_j
                    while line_l > 0 and item_m < len(name_line) - 1:
                        line_l -= 1
                        item_m += 1
                        self.edges.append((name, self.names[line_l][item_m]))
                elif direction == 'DR':
                    line_l, item_m = line_i, item_j
                    while line_l < len(names) - 1 and item_m < len(name_line) - 1:
                        line_l += 1
                        item_m += 1
                        self.edges.append((name, self.names[line_l][item_m]))
                elif direction == 'UL':
                    line_l, item_m = line_i, item_j
                    while line_l > 0 and item_m > 0:
                        line_l -= 1
                        item_m -= 1
                        self.edges.append((name, self.names[line_l][item_m]))
                elif direction == 'DL':
                    line_l, item_m = line_i, item_j
                    while line_l < len(names) - 1 and item_m > 0:
                        line_l += 1
                        item_m -= 1
                        self.edges.append((name, self.names[line_l][item_m]))
    def remove_edge(self, e):
        print("removing", e)
        self.edges.remove(e)
        self.changed = True
    def rename_node(self, old, new):
        if old == new:
            return
        for i in range(len(self.names)):
            for j in range(len(self.names[i])):
                if self.names[i][j] == old:
                    self.names[i][j] = new
        self.all_names.discard(old)
        self.all_names.add(new)
        for i in range(len(self.edges)):
            if self.edges[i][0] == old:
                self.edges[i] = (new, self.edges[i][1])
            if self.edges[i][1] == old:
                self.edges[i] = (self.edges[i][0], new)
        self.changed = True
    def to_digraph(self):
        dot = Digraph(node_attr=dict(splines='curved'))
        for node in self.all_names:
            shape = "box"
            try:
                int(node)
                shape = "circle"
            except ValueError:
                pass
            dot.node(node, shape=shape, regular="true")
        for edge in self.edges:
            dot.edge(edge[0], edge[1])
        return dot
    def reduce(self):
        self.changed = True
        while self.changed:
            self.changed = False
            for edge in self.edges:
                if self.changed:
                    break
                """Remove edges ending in node 1"""
                if edge[1] == str(1):
                    self.remove_edge(edge)
                    break
                """Remove edges x->y if other (y-1)->y exists"""
                try:
                    target = int(edge[1])
                    if (str(target - 1), str(target)) in self.edges and str(target - 1) != edge[0]:
                        self.remove_edge(edge)
                        break
                except ValueError:
                    pass
                """Remove edges x->y if other x->(x+1) exists"""
                try:
                    source = int(edge[0])
                    if (str(source), str(source + 1)) in self.edges and str(source + 1) != edge[1]:
                        self.remove_edge(edge)
                        break
                except ValueError:
                    pass
            """Review nodes with 1 output only"""
            for name in self.all_names:
                if self.changed:
                    break
                outgoings = [edge[1] for edge in self.edges if edge[0] == name]
                if len(outgoings) == 1:
                    try:
                        iname = int(name)
                    except ValueError:
                        iname = None
                    try:
                        oname = int(outgoings[0])
                    except ValueError:
                        oname = None
                    if iname is None and oname is not None:
                        self.rename_node(name, str(oname - 1))
                        name = str(oname - 1)
                    if oname is None and iname is not None:
                        self.rename_node(outgoings[0], str(iname + 1))
                    if self.changed:
                        break
                    ingoings = [edge for edge in self.edges if edge[1] == outgoings[0]]
                    if len(ingoings) != 1:
                        for edge in ingoings:
                            if edge[0] != name:
                                self.remove_edge(edge)
            """Review nodes with 1 input only"""
            for name in self.all_names:
                if self.changed:
                    break
                ingoings = [edge[0] for edge in self.edges if edge[1] == name]
                if len(ingoings) == 1:
                    try:
                        iname = int(ingoings[0])
                    except ValueError:
                        iname = None
                    try:
                        oname = int(name)
                    except ValueError:
                        oname = None
                    if iname is None and oname is not None:
                        self.rename_node(ingoings[0], str(oname - 1))
                    if oname is None and iname is not None:
                        self.rename_node(name, str(iname + 1))
                        name = str(iname + 1)
                    if self.changed:
                        break
                    outgoings = [edge for edge in self.edges if edge[0] == ingoings[0]]
                    if len(outgoings) != 1:
                        for edge in outgoings:
                            if edge[1] != name:
                                self.remove_edge(edge)
            """Remove edges with known numbers if their numbers are not consecutive"""
            for edge in self.edges:
                if self.changed:
                    break
                try:
                    i = int(edge[0])
                    j = int(edge[1])
                    if i != j - 1:
                        self.remove_edge(edge)
                except ValueError:
                    pass

def svg_of_digraph(dot):
    xml = dot.pipe('svg').decode('utf-8')
    i = xml.find('<svg')
    if i == -1:
        raise Exception("svg not found")
    return xml[i:]
