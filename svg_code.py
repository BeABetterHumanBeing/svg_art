# Author: Daniel Gierl
# This is a tool for creating SVG art.

# The tool will attempt (no guarantees) to generate lines that are at most this
# many characters.
MAX_LINE_WIDTH = 80

class XmlBase(object):

  def __init__(self, tag):
    self.tag = tag
    self.params = {}

  def param(self, key, value):
    assert self.isValidParam(key), "{} is not a valid param in class {}" \
      .format(key, type(self).__name__)
    self.params[key] = value
    # Return self so that these commands can be chained.
    return self

  def renderParams(self):
    return ["%s=\"%s\"" % (k, v) for k, v in self.params.items()]

  def render(self, prefix, is_leaf):
    closing_cap = ("/" if is_leaf else "") + ">"
    line = prefix + "<%s" % self.tag
    # If the list of params spills over to a new line, this is the length of
    # the prefix.
    new_line_prefix_len = len(line)
    params = self.renderParams()
    if len(params) == 0:
      return line + closing_cap
    # In the event that we have params, fill lines with them until we go
    # over the line limits.
    idx = 0
    lines = []
    while idx < len(params):
      line += " " + params[idx]
      next_len = 0 if idx == len(params)-1 else len(params[idx+1])
      if len(line) + next_len >= MAX_LINE_WIDTH and idx != len(params)-1:
        lines.append(line)
        line = " " * new_line_prefix_len
      idx += 1
    line += closing_cap
    lines.append(line)
    result = "\n".join([line for line in lines])
    return result

  def isValidParam(self, key):
    return False

  def id(self, id):
    return self.param("id", id)

class XmlLeaf(XmlBase):

  def render(self, prefix):
    return super(XmlLeaf, self).render(prefix, True) + "\n"

class XmlNode(XmlBase):

  def __init__(self, tag):
    super(XmlNode, self).__init__(tag)
    self.children = []

  def child(self, *children):
    for child in children:
      self.children.append(child)
    # Return self so that these commands can be chained.
    return self
  
  def render(self, prefix=""):
    result = super(XmlNode, self).render(prefix, False) + "\n"
    for child in self.children:
      result += child.render(prefix + "  ")
    result += prefix + "</%s>\n" % self.tag
    return result

class Html(XmlNode):
  
  def __init__(self):
    super(Html, self).__init__("html")

  def render(self):
    return "<!DOCTYPE html>\n\n" + super(Html, self).render("")

class Body(XmlNode):

  def __init__(self):
    super(Body, self).__init__("body")

class Svg(XmlNode):

  def __init__(self):
    super(Svg, self).__init__("svg")

  def size(self, width, height):
    self.param("width", "{}".format(width))
    self.param("height", "{}".format(height))
    return self

  def isValidParam(self, key):
    return key in ["width", "height"]

class Path(XmlNode):

  def __init__(self):
    super(Path, self).__init__("path")

  def path(self, *args):
    d = " ".join(args)
    return self.param("d", d)

  def isValidParam(self, key):
    return key in ["id", "stroke", "stroke-width", "d", "fill", "visibility"]

# These fragments are used to generate paths.
def move(x, y):
  return "M {} {}".format(x, y)

def delta_move(dx, dy):
  return "m {} {}".format(dx, dy)

def line(x, y):
  return "L {} {}".format(x, y)

def delta_line(dx, dy):
  return "l {} {}".format(dx, dy)

def horizontal(x):
  return "H {}".format(x)

def delta_horizontal(dx):
  return "h {}".format(dx)

def vertical(y):
  return "V {}".format(y)

def delta_vertical(dy):
  return "v {}".format(dy)

def cubic_bezier(x1, y1, x2, y2, x, y):
  return "C {} {}, {} {}, {} {}".format(x1, y1, x2, y2, x, y)

def delta_cubic_bezier(dx1, dy1, dx2, dy2, dx, dy):
  return "c {} {}, {} {}, {} {}".format(dx1, dy1, dx2, dy2, dx, dy)

def smooth_cubic_bezier(x2, y2, x, y):
  return "S {} {}, {} {}".format(x2, y2, x, y)

def delta_smooth_cubic_bezier(dx2, dy2, dx, dy):
  return "s {} {}, {} {}".format(dx2, dy2, dx, dy)

def quadratic_bezier(x1, y1, x2, y2):
  return "Q {} {}, {} {}".format(x1, y1, x2, y2)

def delta_quadratic_bezier(dx1, dy1, dx2, dy2):
  return "q {} {}, {} {}".format(dx1, dy1, dx2, dy2)

def smooth_quadratic_bezier(x, y):
  return "T {} {}".format(x, y)

def delta_smooth_quadratic_bezier(dx, dy):
  return "t {} {}".format(dx, dy)

def close():
  return "Z"

class Text(XmlNode):

  def __init__(self, text):
    super(Text, self).__init__("text")
    self.text = text

  def render(self, prefix):
    # Small modification of the XmlNode render function, which adds
    # rendering the element's text.
    result = super(XmlNode, self).render(prefix, False) + "\n"
    result += prefix + "  " + self.text + "\n"
    for child in self.children:
      result += child.render(prefix + "  ")
    result += prefix + "</%s>\n" % self.tag
    return result

  def isValidParam(self, key):
    return key in ["x", "y", "dx"]

  def corner(self, x, y):
    self.param("x", "{}".format(x))
    self.param("y", "{}".format(y))
    return self

class Circle(XmlNode):

  def __init__(self):
    super(Circle, self).__init__("circle")

  def isValidParam(self, key):
    return key in ["id", "cx", "cy", "r", "stroke", "stroke-width", "fill"]

  def center(self, cx, cy):
    self.param("cx", "{}".format(cx))
    self.param("cy", "{}".format(cy))
    return self

  def radius(self, r):
    return self.param("r", "{}".format(r))

class Line(XmlNode):

  def __init__(self):
    super(Line, self).__init__("line")

  def isValidParam(self, key):
    return key in ["x1", "x2", "y1", "y2", "stroke", "stroke-width", "id"]

  def start(self, x, y):
    self.param("x1", "{}".format(x))
    self.param("y1", "{}".format(y))
    return self

  def end(self, x, y):
    self.param("x2", "{}".format(x))
    self.param("y2", "{}".format(y))
    return self

class G(XmlNode):

  def __init__(self):
    super(G, self).__init__("g")

  def isValidParam(self, key):
    return key in ["font-size", "font-family", "fill", "stroke",
      "text-anchor", "stroke-width"]

class AnimateMotion(XmlNode):

  def __init__(self):
    super(AnimateMotion, self).__init__("animateMotion")

  def path(self, *args):
    d = " ".join(args)
    return self.param("path", d)

  def isValidParam(self, key):
    return key in ["id", "path", "begin", "dur", "fill", "repeatCount"]

class MPath(XmlLeaf):

  def __init__(self):
    super(MPath, self).__init__("mpath")

  def isValidParam(self, key):
    return key in ["xlink:href"]

  def link(self, id):
    self.param("xlink:href", "#{}".format(id))
    return self

class Animate(XmlNode):

  def __init__(self):
    super(Animate, self).__init__("animate")

  def isValidParam(self, key):
    return key in ["attributeName", "attributeType", "begin", "dur", "from",
        "to", "fill", "id"]

  def do(self, a, b):
    self.param("from", a)
    self.param("to", b)
    return self
