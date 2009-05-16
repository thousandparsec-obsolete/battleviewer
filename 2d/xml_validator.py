"""
Optional XML Validator

This module attempts to provide XML DTD validation support.  This module should not cause
a critical error if PyXML is not installed on the users system.
"""

try:
    from xml.parsers.xmlproc import xmlval
    from xml.parsers.xmlproc import xmlproc
except ImportError, e:
    print 'Not validating, Import Error:', e
    ValidationError = None
else:
    class ValidationError (Exception):
        def __init__ (self, type, message, location):
            self.type = type
            self.message = message
            self.location = location
        def __repr__ (self):
            return "L%s:%s %s: %s" % (self.location[0], self.location[1], self.type, self.message)

    class ErrorHandler (xmlproc.ErrorHandler):
        def location (self):
            return self.locator.get_line(), self.locator.get_column()
        def warning (self, msg):
            raise ValidationError('Warning', msg, self.location())
        def error (self, msg):
            raise ValidationError('Error', msg, self.location())
        def fatal (self, msg):
            raise ValidationError('Fatal', msg, self.location())

def validate_dtd (file):
    if not ValidationError: return # return if we (are assumed to) have not loaded the xml modules
    parser = xmlval.XMLValidator()
    parser.set_error_handler(ErrorHandler(parser))
    parser.parse_resource(file)

if __name__ == '__main__':
    try:
        validate_dtd('./example1.xml')
    except ValidationError, e:
        print repr(e)

