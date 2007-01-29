
class Entity(object):
	def __init__(self, id, name, model, \
			description="", 
 			death=None,
 			firing=None,
 			weapontype=None,
 			weapon=None):
		self.id = id
		self.name = name
		self.model = model
		self.description = description
		self.death = death
		self.firing = firing
		self.weapontype = weapontype
		self.weapon = weapon	

class action(object):
	pass

class log(action):
	"""\
	Log action. Takes a single message which it displays in the log window.
	"""
	def __init__(self, message):
		self.message = message

class death(action)
	"""\
	Causes an entity to die and get removed from the board.

	Prints a log message "<entity> was destroyed."
	"""
	def __init__(self, entity):
		self.entity = entity

class move(action):
	"""\
	Causes an entity to change location on the board.

	Prints a log message "<entity> moved to <position>."
	"""
	def __init__(self, entity, position):
		self.entity = entity
		self.position = position

class fire(action):
	"""\
	Causes an entity to produce a fire animation at something.

	Gets the source entity to play fire animation.
	If weapon is a laser:
		Draws draws a laser fire from source_pixel to dest_pixel.
	If weapon is a torpedo or missle:
		Draws the projectial and moves it from the source_pixel to dest_pixel.

	Prints a log message "<source> fired a <weapon> at <destination>."
	"""
	def __init__(self, source, source_pixel, dest, dest_pixel):
		self.source = source
		self.source_pixel = pixel
		self.dest = dest
		self.dest_pixel = pixel

class damage(action):
	"""\
	Causes an entity to take damage.

	Gets dest entity to play damaged animation.
	Makes a little number red number which floats off the entity (ala Rollercoaster Tycoon when you build something).

	Prints a log message "<source> was damaged for <amount> HP."
	"""
	def __init__(self, entity, amount):
		self.entity = entity
		self.amount = amount
