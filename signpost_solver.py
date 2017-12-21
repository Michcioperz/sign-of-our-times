#!/usr/bin/env python3
import string, functools
from graphviz import Digraph

class TathamSavefile(list):
    def one_by_key(self, key):
        values = self.multiple_by_key(key)
        if len(values) > 1:
            print("warning: trimming one_by_key")
        return values[0]
    def multiple_by_key(self, key):
        return [value for (k, value) in self if k == key]
    def __init__(self, content):
        """Loads savefile from Tatham's puzzles as a list of key-value tuples"""
        for line in content.strip().split('\n'):
            key, length, value = line.strip().split(':', 2)
            if len(value) != int(length):
                print("warning: mismatched length and len(value) in line: {!r}".format(line))
            self.append((key.strip(), value))


class Signpost(object):
    savefile_directions = {
            'a': 'U',
            'b': 'UR',
            'c':  'R',
            'd': 'DR',
            'e': 'D',
            'f': 'DL',
            'g':  'L',
            'h': 'UL',
            }
    @classmethod
    def from_savefile(cls_, savefile_content):
        config = TathamSavefile(savefile_content)
        size = [int(a) for a in config.one_by_key("PARAMS").rstrip('c').split('x')]
        puzzle_desc = config.one_by_key("DESC")
        names_unsplit = ''.join([" " if char in string.ascii_letters else char for char in puzzle_desc]).split(' ')[:-1]
        last_index = names_unsplit.index(str(size[0] * size[1]))
        assert(len(names_unsplit) == size[0] * size[1])
        names = [names_unsplit[size[0] * i:size[0] * (i + 1)] for i in range(size[1])]
        directions_unsplit = list(map(cls_.savefile_directions.get, [char for char in puzzle_desc if char in string.ascii_letters]))
        directions_unsplit[last_index] = ''
        assert(len(directions_unsplit) == size[0] * size[1])
        directions = [directions_unsplit[size[0] * i:size[0] * (i + 1)] for i in range(size[1])]
        # TODO: apply MOVE directives
        return cls_(directions, names)
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
            for i in range(3, self.size*self.size + 1):
                if self.changed:
                    break
                first_name = str(i-2)
                middle_name = str(i-1)
                last_name = str(i)
                if first_name in self.all_names and last_name in self.all_names and middle_name not in self.all_names:
                    middles = [name for name in self.all_names if (first_name, name) in self.edges and (name, last_name) in self.edges]
                    if len(middles) == 1:
                        self.rename_node(name, middle_name)

def svg_of_digraph(dot):
    xml = dot.pipe('svg').decode('utf-8')
    i = xml.find('<svg')
    if i == -1:
        raise Exception("svg not found")
    return xml[i:]
