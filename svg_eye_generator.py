# Author: Daniel Gierl
# This is a tool for creating SVG art.

output = Html()
print output.render()

print "\n\n"

def html(content):
	return "<!DOCTYPE html>\n<html>\n" + content + "</html>\n"

def body(content):
	return "<body>\n" + content + "</body>\n"

def svg(content, width = 100, height = 100):
	header = "<svg height=\"%d\" width=\"%d\">\n" % (height, width)
	message = "Sorry, your browser does not support inline SVG.\n"
	return header + content + message + "</svg>\n"

def g(content, stroke = None, stroke_width = None, fill = "none",
	  font_size = None, font_family = None, text_anchor = None):
	args = ""
	if stroke is not None:
		args += "stroke=\"%s\" " % stroke
	if stroke_width is not None:
		args += "stroke-width=\"%d\" " % stroke_width
	if fill is not None:
		args += "fill=\"%s\" " % fill
	if font_size is not None:
		args += "font-size=\"%s\" " % font_size
	if font_family is not None:
		args += "font-family=\"%s\" " % font_family
	if text_anchor is not None:
		args += "text-anchor=\"%s\" " % text_anchor
	return ("<g %s>\n" % args) + content + "</g>\n"

def circle(id = None, cx = None, cy = None, r = None):
	args = ""
	if id is not None:
		args += "id=\"%s\" " % id
	if cx is not None:
		args += "cx=\"%d\" " % cx
	if cy is not None:
		args += "cy=\"%d\" " % cy
	if r is not None:
		args += "r=\"%d\" " % r
	return "<circle %s/>\n" % args

def text(content, x = None, y = None, dx = None, dy = None):
	args = ""
	if x is not None:
		args += "x=\"%d\" " % x
	if y is not None:
		args += "y=\"%d\" " % y
	if dx is not None:
		args += "dx=\"%d\" " % dx
	if dy is not None:
		args += "dy=\"%d\" " % dy
	return ("<text %s>" % args) + content + "</text>\n"

def path(id = None, d = None, stroke = None, stroke_width = None, fill = "none"):
	args = ""
	if id is not None:
		args += "id=\"%s\" " % id
	if d is not None:
		args += "d=\"%s\" " % " ".join(d)
	if stroke is not None:
		args += "stroke=\"%s\" " % stroke
	if stroke_width is not None:
		args += "stroke-width=\"%d\" " % stroke_width
	if fill is not None:
		args += "fill=\"%s\" " % fill
	return "<path %s/>\n" % args

def move(x, y):
	return "M %d %d" % (x, y)

def line(x, y):
	return "l %d %d" % (x, y)

def bezier(x1, y1, x2, y2):
	return "q %d %d %d %d" % (x1, y1, x2, y2)

# TEST
circles = ""
circles += circle(
	id = "pointA",
	cx = 100, cy = 350, r = 3)
circles += circle(
	id = "pointB",
	cx = 250, cy = 50, r = 3)
circles += circle(
	id = "pointC",
	cx = 400, cy = 350, r = 3)

text_content = ""
text_content += text(
	x = 100, y = 350,
	dx = -30,
	content = "A")
text_content += text(
	x = 250, y = 50,
	dx = -10,
	content = "B")
text_content += text(
	x = 400, y = 350,
	dx = 30,
	content = "C")

content = ""
content += path(
	id = "lineAB",
	d = (move(100, 350),
		 line(150, -300)),
	stroke = "red",
	stroke_width = 3)
content += path(
	id = "lineBC",
	d = (move(250, 50),
		 line(150, 300)),
	stroke = "red",
	stroke_width = 3)
content += path(
	d = (move(175, 200),
		 line(150, 0)),
	stroke = "green",
	stroke_width = 3)
content += path(
	d = (move(100, 350),
		 bezier(150, -300, 300, 0)),
	stroke = "blue",
	stroke_width = 5)
content += g(
	stroke = "black",
	stroke_width = 3,
	fill = "black",
	content = circles)
content += g(
	font_size = "30",
	font_family = "sans-serif",
	fill = "black",
	stroke = "none",
	text_anchor = "middle",
	content = text_content)
result = \
	html(
	body(
	svg(width = 1000, height = 1000,
		content = content)))

print "Result:"
print result
with open("result.html", "w") as f:
	f.write(result)
	print "Wrote to result.html"