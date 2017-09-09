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

	def child(self, child):
		self.children.append(child)
		# Return self so that these commands can be chained.
		return self
	
	def render(self, prefix):
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

class Path(XmlLeaf):

	def __init__(self):
		super(Path, self).__init__("path")

	def path(self, *args):
		d = " ".join(args)
		return self.param("d", d)

	def isValidParam(self, key):
		return key in ["id", "stroke", "stroke-width", "d", "fill"]

# These fragments are used to generate paths.
def move(x, y):
	return "M %d %d" % (x, y)

def line(x, y):
	return "l %d %d" % (x, y)

def bezier(x1, y1, x2, y2):
	return "q %d %d %d %d" % (x1, y1, x2, y2)

class Text(XmlNode):

	def __init__(self, text):
		super(Text, self).__init__("text")
		self.text = text

	def render(self, prefix):
		# Small modification of the XmlNode render function.
		result = super(XmlNode, self).render(prefix, False) + "\n"
		result += prefix + "  " + self.text + "\n"
		result += prefix + "</%s>\n" % self.tag
		return result

	def child(self, child):
		assert False, "<text></text> cannot have children"

	def isValidParam(self, key):
		return key in ["x", "y", "dx"]

	def corner(self, x, y):
		self.param("x", "{}".format(x))
		self.param("y", "{}".format(y))
		return self

class Circle(XmlLeaf):

	def __init__(self):
		super(Circle, self).__init__("circle")

	def isValidParam(self, key):
		return key in ["id", "cx", "cy", "r"]

	def center(self, cx, cy):
		self.param("cx", "{}".format(cx))
		self.param("cy", "{}".format(cy))
		return self

	def radius(self, r):
		return self.param("r", "{}".format(r))

class G(XmlNode):

	def __init__(self):
		super(G, self).__init__("g")

	def isValidParam(self, key):
		return key in ["font-size", "font-family", "fill", "stroke",
			"text-anchor", "stroke-width"]

# TEST SVG from W3Schools
output = \
	Html().child(
	Body().child(
	Svg().param("width", 1000).param("height", 1000).child(
		Path()
			.id("lineAB")
			.param("stroke", "red")
			.param("stroke-width", "3")
			.path(move(100, 350), line(150, -300))).child(
		Path()
			.id("lineBC")
			.param("stroke", "red")
			.param("stroke-width", "3")
			.path(move(250, 50), line(150, 300))).child(
		Path()
			.param("stroke", "green")
			.param("stroke-width", "3")
			.path(move(175, 200), line(150, 0))).child(
		Path()
			.param("stroke", "blue")
			.param("stroke-width", "5")
			.param("fill", "none")
			.path(move(100, 350), bezier(150, -300, 300, 0))).child(
		G()
			.param("stroke", "black")
			.param("stroke-width", "3")
			.param("fill", "black").child(
			Circle()
				.param("id", "pointA")
				.center(100, 350)
				.radius(3)).child(
			Circle()
				.param("id", "pointB")
				.center(250, 50)
				.radius(3)).child(
			Circle()
				.param("id", "pointC")
				.center(400, 350)
				.radius(3))).child(
		G()
			.param("font-size", "30")
			.param("font-family", "sans-serif")
			.param("fill", "black")
			.param("stroke", "none")
			.param("text-anchor", "middle").child(
			Text("A")
				.corner(100, 350)
				.param("dx", "-30")).child(
			Text("B")
				.corner(250, 50)
				.param("dx", "-10")).child(
			Text("C")
				.corner(400, 350)
				.param("dx", "30")))))
result = output.render()

print "Result:"
print result
with open("result.html", "w") as f:
	f.write(result)
	print "Wrote to result.html"