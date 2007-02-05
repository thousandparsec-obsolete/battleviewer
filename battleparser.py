
import xml.parsers.expat

class Parser(object):
	class Battle:
		"""\
		Contains everything you need to know about a battle.

		"""
		def __init__(self, sides, rounds, version):
			if not isinstance(sides[0], Parser.Sides):
				raise TypeError("Sides must be sides...")
			if not isinstance(rounds[0], Parser.Rounds):
				raise TypeError("Rounds must be rounds...")

			self.version = version
			self.sides   = sides[0]
			self.rounds  = rounds[0]

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
		def __init__(self, id=None, name=None, model=None, \
				description="", 
				weaponpoints=[],
				death=None,
				firing=None,
				weapontype=None,
				weapon=None):
			if id is None or name is None or model is None:
				raise TypeError("Entity requires id, name and model...")

			self.id = id
			self.name = name
			self.model = model
			self.description = description
			self.weaponpoints = weaponpoints
			self.death = death
			self.firing = firing
			self.weapontype = weapontype
			self.weapon = weapon	
		def __repr__(self):
			return "<Entity %s - '%s'>" % (self.id, self.name)
		__str__ = __repr__

	class Weaponpoints(list):
		group="weaponpoints"
		def __init__(self, pixels):
			for pixel in pixels:
				self.append(pixel)

		def __repr__(self):
			return "<WeaponPoints %s>" % (list.__repr__(self))

	class Pixel(list):
		group="pixels"
		def __init__(self, data):
			for i in data.split(','):
				self.append(int(i))

		def __repr__(self):
			return "<Pixel %s>" % list.__repr__(self)

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
		def __init__(self, data=""):
			self.data = data
		def __repr__(self):
			return "<Log '%s'>" % (self.data,)

	class Death(Action):
		"""\
		Causes an entity to die and get removed from the board.

		Prints a log message "<reference> was destroyed."
		"""
		def __init__(self, ref):
			self.reference = ref

		def __repr__(self):
			return "<Death '%s'>" % (self.reference,)

	class Move(Action):
		"""\
		Causes an reference to change location on the board.

		Prints a log message "<reference> moved to <position>."
		"""
		def __init__(self, ref, position):
			self.reference = ref

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
			self.source = source[0]
			self.destination = destination[0]

		def __repr__(self):
			return "<Fire %s %s>" % (self.source, self.destination)


	class Damage(Action):
		"""\
		Causes an reference to take damage.

		Gets dest reference to play damaged animation.
		Makes a little number red number which floats off the reference (ala Rollercoaster Tycoon when you build something).

		Prints a log message "<source> was damaged for <amount> HP."
		"""
		def __init__(self, ref, amount):
			self.reference = ref
			self.amount = amount

		def __repr__(self):
			return "<Damage '%s' %s>" % (self.reference, self.amount)

	class Source(object):
		group="source"
		def __init__(self, ref):
			self.reference = ref

		def __repr__(self):
			return "<%s %s>" % (self.__class__.__name__, self.reference)

	class Destination(Source):
		group="destination"

	def __init__(self):
		self.mode = []
		self.attr = []
		self.data = []

	def StartElementHandler(self, name, attr):
		self.mode.append(getattr(self, name.title(), None))

		self.attr.append({})
		# Need this to convert from Unicode to ASCII
		for key, value in attr.items():
			self.attr[-1][str(key)] = value

		self.data.append(None)

	def EndElementHandler(self, name):
		if self.mode[-1] != getattr(self, name.title(), None):
			raise ValueError("Element matching error")

		mode = self.mode.pop(-1)
		attr = self.attr.pop(-1)
		data = self.data.pop(-1)

		if mode is None:
			if not data is None:
				self.attr[-1][str(name)] = data
			else:
				for name, value in attr.items():
					self.attr[-1][str(name)] = value
			return

		if not data is None:
			attr['data'] = data
	
		try:
			obj = mode(**attr)
		except Exception, e:
			print mode
			raise

		if len(self.mode) > 0:
			if not self.attr[-1].has_key(obj.group):
				self.attr[-1][obj.group] = []
			self.attr[-1][obj.group].append(obj)
		else:
			self.objects = obj

	def CharacterDataHandler(self, data):
		data = data.strip()
		if len(data) > 0:
			self.data[-1] = data

	def CreateParser(cls):
		p = xml.parsers.expat.ParserCreate()
		c = cls()

		for name in cls.__dict__.keys():
			if name.startswith('_') or name == "CreateParser":
				continue
			
			value = getattr(c, name)
			try:
				if callable(value):
					setattr(p, name, value)
			except Exception, e:
				pass

		c.parser = p
		c.Parse = p.Parse
		c.ParseFile = p.ParseFile

		return c
	CreateParser = classmethod(CreateParser)

if __name__ == "__main__":
	import sys

	parser = Parser.CreateParser()
	print parser
	parser.ParseFile(file("example1.xml", "r"))

	battle = parser.objects
	for side in battle.sides.keys():
		print side
		for name, entity in battle.sides[side].items():
			print entity, entity.weaponpoints
	for round in battle.rounds:
		print round

