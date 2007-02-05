
import elementtree.ElementTree as ET
import os.path

class BattleMedia(object):
	optional = ['death', 'firing', 'weapontype', 'weapon', 'weaponpoints']
	paths = ['model', 'death', 'firing']

	def __init__(self, f):
		tree = ET.parse(file(os.path.join(f, 'types.xml'), 'r'))
		self.root = tree.getroot()

		if self.root.tag.strip() != "battlemedia":
			raise TypeError("Not a battlemedia file.")

		for node in self.root:
			id = node.attrib['id']
		
			class new(object):
				type = id
				weapontype = None
				weaponpoints = []

			for value in node.getchildren():
				tag = value.tag.strip()
				text = value.text.strip()

				if tag in self.paths:
					setattr(new, tag, os.path.join(f, text))
				elif len(text) > 0:
					setattr(new, tag, text)
				else:
					setattr(new, tag, value)

				print dir(new)

			tag = node.tag.strip()

			globals()[id] = new

	def weaponpoints_set(self, value):
		points = []
		for weaponpoint in value:
			if weaponpoint.tag.strip() != "pixel":
				raise TypeError("Weapon Points must list pixels.")

			point = []
			for p in weaponpoint.text.split(','):
				point.append(int(p))

			points.append(point)
		self._weaponpoints = points
	def weaponpoints_get(self):
		return self._weaponpoints
	weaponpoints = property(weaponpoints_get, weaponpoints_set)

class Parser(object):
	class Battle:
		"""\
		Contains everything you need to know about a battle.
		"""
		def __init__(self, sides, rounds, version, media):
			if not isinstance(sides[0], Parser.Sides):
				raise TypeError("Sides must be sides...")
			if not isinstance(rounds[0], Parser.Rounds):
				raise TypeError("Rounds must be rounds...")

			self.version = version
			self.sides   = sides[0]
			self.rounds  = rounds[0]
			self.media   = media

	class Sides(dict):
		group="sides"
		def __init__(self, sides=[]):
			for side in sides:
				if not isinstance(side, Parser.Side):
					raise TypeError("Can only have Sides in a Sides..")

				self[str(side.id)] = side

		def __repr__(self):
			return "<Sides %s>" % self.keys()
		__str__ = __repr__

	class Side(dict):
		group="sides"
		def __init__(self, id=None, entities=[]):
			if id is None:
				raise TypeError("Sides must have an id.")
			self.id = id

			for entity in entities:
				if not isinstance(entity, Parser.Entity):
					raise TypeError("Can only have Entities in a Side.")
				self[str(entity.id)] = entity

		def __repr__(self):
			return "<Side id=%s entities=%s>" % (self.id, dict.__repr__(self))
		__str__ = __repr__

	class Entity(object):
		group="entities"
		def __init__(self, id=None, name=None, type=None, \
				description=""):
			if id is None or name is None or type is None:
				raise TypeError("Entity requires id, name and type...")

			class new(Parser.Entity, globals()[type]):
				pass

			self.__class__ = new

			self.id = id
			self.name = name
			self.type = type
		def __repr__(self):
			return "<Entity (%s) %s - '%s'>" % (self.type, self.id, self.name)
		__str__ = __repr__

	class Rounds(list):
		group="rounds"
		def __init__(self, rounds=[]):
			for round in rounds:
				if not isinstance(round, Parser.Round):
					raise TypeError("Can only have Rounds in a Rounds.")
				self.append(round)

	class Round(list):
		group="rounds"
		def __init__(self, number=None, actions=[]):
			self.number = number
			self.actions = actions

		def __repr__(self):
			return "<Round %s %s>" % (self.number, self.actions)

	class Action(object):
		group="actions"
		
		def __repr__(self):
			return "<%s>" % (self.__class__.__name__)

	class Log(Action):
		"""\
		Log Action. Takes a single message which it displays in the log window.
		"""
		def __init__(self, text=""):
			self.data = text
		def __repr__(self):
			return "<Log '%s'>" % (self.text,)

	class Death(Action):
		"""\
		Causes an entity to die and get removed from the board.

		Prints a log message "<reference> was destroyed."
		"""
		def __init__(self, reference):
			self.reference = reference

		def __repr__(self):
			return "<Death '%s'>" % (self.reference,)

	class Move(Action):
		"""\
		Causes an reference to change location on the board.

		Prints a log message "<reference> moved to <position>."
		"""
		def __init__(self, reference, position):
			self.reference = reference

			self.position = []
			for i in position.split(','):
				self.position.append(int(i))

		def __repr__(self):
			return "<Move %s %s>" % (self.reference, self.position)

	class Fire(Action):
		"""\
		Causes an reference to produce a fire animation at something.

		Gets the source reference to play fire animation.
		If weapon is a laser:
			Draws draws a laser fire from source_pixel to dest_pixel.
		If weapon is a torpedo or missle:
			Draws the projectial and moves it from the source_pixel to dest_pixel.

		Prints a log message "<source> fired a <weapon> at <destination>."
		"""
		def __init__(self, source, destination):
			self.source = source
			self.destination = destination

		def __repr__(self):
			return "<Fire %s %s>" % (self.source, self.destination)

	class Damage(Action):
		"""\
		Causes an reference to take damage.

		Gets dest reference to play damaged animation.
		Makes a little number red number which floats off the reference (ala Rollercoaster Tycoon when you build something).

		Prints a log message "<source> was damaged for <amount> HP."
		"""
		def __init__(self, reference, amount):
			self.reference = reference
			self.amount = amount

		def __repr__(self):
			return "<Damage '%s' %s>" % (self.reference, self.amount)

	def CreateParser(cls):
		return cls()
	CreateParser = classmethod(CreateParser)

	def ParseFile(self, file):
		tree = ET.parse(file)
		self.root = tree.getroot()

		media = self.root.attrib['media']
		self.media   = BattleMedia(media)

		self.objects = self.ConvertNode(self.root)

	def ConvertNode(self, obj):
		d = {}

		children = obj.getchildren()
		for child in obj.getchildren():
			r = self.ConvertNode(child)

			if hasattr(r, "group"):
				if not d.has_key(r.group):
					d[r.group] = []
				d[r.group].append(r)
			else:
				print child.tag, r
				d[child.tag] = r['text']

		if len(obj.attrib) > 0:
			if obj.attrib.has_key('ref'):
				d['text'] = obj.attrib['ref']
			else:
				d.update(obj.attrib)
		elif obj.text and len(obj.text.strip()) > 0:
			d['text'] = obj.text.strip()

		tag = obj.tag.strip().title()
		if hasattr(Parser, tag):
			return getattr(Parser, tag)(**d)
		return d

if __name__ == "__main__":
	import sys

	parser = Parser.CreateParser()
	print parser
	parser.ParseFile(file("example1.xml", "r"))

	battle = parser.objects
	for side in battle.sides.keys():
		print side
		for name, entity in battle.sides[side].items():
			print entity, entity.model
	for round in battle.rounds:
		print round


