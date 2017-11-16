This Python web thing, given a [Signpost/Pfeilpfad puzzle](https://www.chiark.greenend.org.uk/~sgtatham/puzzles/js/signpost.html), tries to simplify and reduce it, solve it if naively possible or present the remaining path candidates as a graph.

The web server does not perform any input validation at the time.

The web server uses Flask framework (`pip install flask`) and GraphViz-Python interface (`pip install graphviz`) and depends on GraphViz to be installed on the system.

When inputting the puzzle, the id of a node can be either a number (then it will be assumed that this is the node's order in the path) or anything else you want to name it. If the name is not provided, it will be filled with `[row, column]`.

The direction is the direction of the arrow and it should match a regular expression `[UD]?[LR]?` where the letters represent Up, Down, Left, Right.
