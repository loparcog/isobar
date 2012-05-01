"""Testing pydoc"""

import sys
import random
import itertools

from isobar.pattern.core import *
from isobar.key import *
from isobar.util import *

class PChanged(Pattern):
	""" PChanged: Outputs a 1 if the value of a pattern has changed. """

	def __init__(self, source):
		self.source = source
		self.current = Pattern.value(self.source)

	def next(self):
		next = Pattern.value(self.source)
		rv = 0 if next == self.current else 1
		self.current = next
		return rv

class PDiff(Pattern):
	""" PDiff: Outputs the difference between the current and previous values of an input pattern """

	def __init__(self, source):
		self.source = source
		self.current = Pattern.value(self.source)

	def next(self):
		next = Pattern.value(self.source)
		rv = next - self.current
		self.current = next
		return rv

class PAbs(Pattern):
	""" PAbs: Absolute value of <input> """

	def __init__(self, input):
		self.input = input

	def next(self):
		next = Pattern.value(self.input)
		if next is not None:
			return abs(next)
		return next

class PReverse(Pattern):
	""" reverses a finite sequence """

	def __init__(self, input):
		self.input = input
		self.values = reversed(list(input))

	def next(self):
		return self.values.next()

class PDelay(Pattern):
	""" outputs the next value of patternA after patternB ticks """

	def __init__(self, source, delay):
		self.source = source
		self.delay = delay
		self.counter = Pattern.value(self.delay)

	def next(self):
		self.counter -= 1
		if self.counter < 0:
			self.counter = Pattern.value(self.delay)
			return Pattern.value(self.source)

class PMap(Pattern):
	""" PMap: Apply an arbitrary function to an input pattern.
		      Will pass any additional arguments, which can also be patterns.

		>>> PMap(PSeries(), lambda value: value * value).nextn(16)
		[0, 1, 4, 9, 16, 25, 36, 49, 64, 81, 100, 121, 144, 169, 196, 225]

		>>> PMap(PSeries(), pow, PSeries()).nextn(16)
		[1, 1, 4, 27, 256, 3125, 46656, 823543, 16777216, 387420489, 10000000000, ... ]
		"""

	def __init__(self, input, operator, *args, **kwargs):
		self.input = input
		self.operator = operator
		self.args = args
		self.kwargs = kwargs

	def next(self):
		args = [ Pattern.value(value) for value in self.args ]
		kwargs = dict((key, Pattern.value(value)) for key, value in self.kwargs.items())
		value = self.input.next()
		print "applying sin to %f" % value
		rv = self.operator(value, *args, **kwargs)
		print "output is %f" % rv
		return rv

class PMapEnumerated(PMap):
	""" PMapEnumerated: Apply arbitrary function to input, passing a counter.

		>>> PMapEnumerated(PSeq([ 1, 11, 111 ]), lambda n, value: n * value).nextn(16)
		[0, 11, 222, 3, 44, 555, 6, 77, 888, 9, 110, 1221, 12, 143, 1554, 15]
		"""

	def __init__(self, *args):
		PMap.__init__(self, *args)
		self.counter = 0

	def next(self):
		args = [ Pattern.value(value) for value in self.args ]
		kwargs = dict((key, Pattern.value(value)) for key, value in self.kwargs.items())
		value = self.input.next()
		rv = self.operator(self.counter, value, *args, **kwargs)
		self.counter += 1
		return rv
		
class PLinLin(PMap):
	""" PLinLin: Map <input> from linear range [a,b] to linear range [c,d].

		>>> p = PLinLin(PWhite(), 0, 1, -50, 50)
		>>> p.nextn(16)
		[-34.434991496625955, -33.38823791706497, 42.153457333940267, 16.692545937573783, ... -48.850511242044604 ]
		"""

	def linlin(self, value, from_min = 0, from_max = 1, to_min = 0, to_max = 1):
		norm = float(value - from_min) / (from_max - from_min)
		return norm * float(to_max - to_min) + to_min

	def __init__(self, input, *args):
		PMap.__init__(self, input, self.linlin, *args)

class PLinExp(PMap):
	""" PLinExp: Map <input> from linear range [a,b] to exponential range [c,d].

		>>> p = PLinExp(PWhite(), 0, 1, 40, 20000)
		>>> p.nextn(16)
		"""

	def linexp(self, value, from_min = 0, from_max = 1, to_min = 1, to_max = 10):
		if value < from_min: return to_min
		if value > from_max: return to_max
		return ((to_max / to_min) ** ((value - from_min) / (from_max - from_min))) * to_min;

	def __init__(self, input, *args):
		PMap.__init__(self, input, self.linexp, *args)

class PRound(PMap):
	""" PRound: Round <input> to N decimal places.

		>>> p = PLinExp(PWhite(), 0, 1, 40, 20000)
		>>> p.nextn(16)
		"""
	def __init__(self, input, *args):
		PMap.__init__(self, input, round, *args)

class PPad(Pattern):
	""" PPad: Pad <pattern> with rests until it reaches length <length>.
		"""

	def __init__(self, pattern, length):
		self.pattern = pattern
		self.length = length
		self.count = 0

	def next(self):
		try:
			rv = self.pattern.next()
		except:
			if self.count >= self.length:
				raise StopIteration
			rv = None

		self.count += 1
		return rv

class PPadToMultiple(Pattern):
	""" PPadToMultiple: Pad <pattern> with rests until its length is divisible by <multiple>.
		Enforces a minimum padding of <minimum_pad>.

		Useful to create patterns which occupy a whole number of bars.
		"""

	def __init__(self, pattern, multiple, minimum_pad = 0):
		self.pattern = pattern
		self.multiple = multiple
		self.minimum_pad = minimum_pad
		self.count = 0
		self.padcount = 0
		self.terminated = False

	def next(self):
		try:
			rv = self.pattern.next()
		except:
			if self.padcount >= self.minimum_pad and (self.count % self.multiple == 0):
				raise StopIteration
			else:
				rv = None
				self.padcount += 1

		self.count += 1
		return rv
