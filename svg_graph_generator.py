from svg_code import *
import math

# Whether to print the contents of the SVG to the terminal when saving to file.
LOG_SVG = False
# Whether, when rendering the graph, to put the SVG in an HTML skeleton or not.
RENDER_HTML = False
# Distance, in pixels, from the center of the SVG to its edge.
CENTER = 20
SECONDS_PER_MOVE = 0.5
NODE_RADIUS = 5
MAX_STROKE_WIDTH = 6
# When nodes get small, we don't want their stroke width overpowering them.
STROKE_WIDTH = min(MAX_STROKE_WIDTH, NODE_RADIUS / 2)
# When the SVG gets really small, we don't want the nodes getting clipped by its
# edges.
RADIUS = min(CENTER * 2 / 3, CENTER - NODE_RADIUS - STROKE_WIDTH)

def polar2cartesian(r, tau):
  t = tau - 0.25  # Factor to rotate shape so 0 is up.
  factor = 2 * math.pi  # Factor to get to pi-based system.
  x = CENTER + r * math.cos(factor * t)
  y = CENTER + r * math.sin(factor * t)
  return x, y

class Move(object):

  def __init__(self, name, prev_move=None):
    self.name = name
    self.prev_move = prev_move

class Node(object):

  def __init__(self, name, r, tau):
    self.name = name
    self.positions = [(r, tau)]
    self.moves = []
    self.edges = []
    self.svg = None

  # Deprecated. Remove after edges are corrected.
  def getStartPosition(self):
    return polar2cartesian(*self.positions[0])

  def addPosition(self, r, tau, prev_move):
    # Create move name before adding a new position.
    move_name = "{}_move_{}".format(self.name, len(self.positions))
    self.positions.append((r, tau))
    self.moves.append(Move(move_name, prev_move))
    return move_name

  def getPath(self, idx):
    start_x, start_y = polar2cartesian(*self.positions[idx])
    end_x, end_y = polar2cartesian(*self.positions[idx + 1])
    return start_x, start_y, end_x, end_y

  def getSVG(self):
    if self.svg is not None:
      return self.svg
    # Create the node itself.
    self.svg = Circle() \
      .id(self.name) \
      .param("stroke", "black") \
      .param("stroke-width", STROKE_WIDTH) \
      .param("fill", "red") \
      .center(*polar2cartesian(*self.positions[0])) \
      .radius(NODE_RADIUS)

    # Add the node's various moves.
    for i in range(len(self.moves)):
      # Determine when the move happens.
      prev_move = self.moves[i].prev_move
      begin = "0s"
      if prev_move is not None:
        begin = "{}.end".format(prev_move)

      # Get the motion itself.
      start_x, start_y, end_x, end_y = self.getPath(i)

      # Each move is composed for 2 + 2E animations, where E is the number of
      # edges leading out of the node. It's a damn pity you can't target
      # multiple attributes, but oh well. They all have the same timing,
      # differing only in what they target.
      anim_cx = getBaseAnimation(begin)
      anim_cx.id(self.moves[i].name)  # One 'master' animation is given an id.
      anim_cx.param("attributeName", "cx")
      anim_cx.do(start_x, end_x)
      self.svg.child(anim_cx)
      anim_cy = getBaseAnimation(begin)
      anim_cy.param("attributeName", "cy")
      anim_cy.do(start_y, end_y)
      self.svg.child(anim_cy)
      for edge, is_forward in self.edges:
        num = "1" if is_forward else "2"
        anim_x = getBaseAnimation(begin)
        anim_x.param("attributeName", "x{}".format(num))
        anim_x.do(start_x, end_x)
        edge.getSVG().child(anim_x)
        anim_y = getBaseAnimation(begin)
        anim_y.param("attributeName", "y{}".format(num))
        anim_y.do(start_y, end_y)
        edge.getSVG().child(anim_y)

    return self.svg

class Edge(object):

  def __init__(self, node1, node2):
    self.node1 = node1
    self.node2 = node2
    node1.edges.append((self, True))  # Bool indicates edge direction.
    node2.edges.append((self, False))
    self.svg = None

  def getSVG(self):
    if self.svg is not None:
      return self.svg
    self.svg = Line() \
      .param("stroke", "black") \
      .param("stroke-width", STROKE_WIDTH) \
      .start(*self.node1.getStartPosition()) \
      .end(*self.node2.getStartPosition())
    return self.svg

class Graph(object):

  def __init__(self, name):
    self.name = name
    self.nodes = []
    self.edges = []
    self.svg = None

  def addNode(self, node):
    self.nodes.append(node)

  def addEdge(self, edge):
    self.edges.append(edge)

  # Creates the SVG rules for this graph.
  def getSVG(self):
    if self.svg is not None:
      return self.svg
    g = G()
    for edge in self.edges:
      g.child(edge.getSVG())
    for node in self.nodes:
      g.child(node.getSVG())
    if RENDER_HTML:
      self.svg = Html().child(
        Body().child(
          Svg()
            .param("width", CENTER * 2)
            .param("height", CENTER * 2)
            .child(g)))
    else:
      self.svg = Svg() \
        .param("width", CENTER * 2) \
        .param("height", CENTER * 2) \
        .child(g)
    return self.svg

  # Renders the rules to a file.
  def render(self):
    result = self.getSVG().render()
    if LOG_SVG:
      print "Rendering result:"
      print result
    extension = "html" if RENDER_HTML else "svg"
    filename = "{}.{}".format(self.name, extension)
    with open(filename, "w") as f:
      f.write(result)
      print "Wrote to {}".format(filename)

def getBaseAnimation(begin):
  return Animate() \
    .param("dur", "{}s".format(SECONDS_PER_MOVE)) \
    .param("begin", begin) \
    .param("fill", "freeze") \
    .param("attributeType", "XML")

def addMove(graph, vertices, coprime, n, prev_move):
  curr_idx = graph.nodes[n].positions[-1][1] * vertices
  next_idx = (curr_idx - coprime) % vertices
  move_name = graph.nodes[n].addPosition(
    RADIUS, next_idx / float(vertices), prev_move)
  return move_name

def generateMoveSequence(vertices, coprime):
  seq = []
  idx = -1 + coprime
  while idx != vertices - 1:
    seq.append(idx)
    idx = (idx + coprime) % vertices
  return seq

def numMoveRepetitions(vertices, coprime):
  num = 1
  idx = coprime
  while idx != 0:
    num += 1
    idx = (idx + coprime) % vertices
  return num

# Code for generating displacing ring graphs. They have an equilateral with
# some number of vertices, except one has been removed. The nodes then serially
# move into the displaced spot (thereby changing the location of the
# displacement) continuously. To determine which node moves first, a second
# number, co-prime to the number of vertices, is supplied.
def generateDisplacingRingGraph(name, vertices, coprime):
  graph = Graph(name)
  for i in range(vertices - 1):
    graph.addNode(Node("n{}".format(i), RADIUS, i / float(vertices)))
  for i in range(vertices - 1):
    n1 = graph.nodes[i]
    n2 = graph.nodes[(i + 1) % (vertices - 1)]
    graph.addEdge(Edge(n1, n2))

  # Number of times each node needs to move to get back to where it started.
  # (Minus 1 because it loops.)
  prev_move = None
  for j in range(numMoveRepetitions(vertices, coprime)):
    # Order of rotations.
    for i in generateMoveSequence(vertices, coprime):
      prev_move = addMove(graph, vertices, coprime, i, prev_move)
  # Lastly, let's tie the last motion to the first, so that the entire thing
  # cycles indefinitely. It still needs to start with 0s (to get the entire
  # animation moving).
  # graph.nodes[-1 + coprime].moves[0].prev_move = "0s;{}".format(prev_move)
  return graph

VERTICES = 5
COPRIME = 2

graph = generateDisplacingRingGraph("pentagon", VERTICES, COPRIME)
graph.render()

VERTICES = 4
COPRIME = 1

graph = generateDisplacingRingGraph("square", VERTICES, COPRIME)
graph.render()

VERTICES = 3
COPRIME = 1

graph = generateDisplacingRingGraph("triangle", VERTICES, COPRIME)
graph.render()
