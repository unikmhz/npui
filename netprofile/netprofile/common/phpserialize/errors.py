# -*- coding: utf-8 -*-

class PhpSerializationError(ValueError):
    pass

class PhpUnserializationError(ValueError):
    pass

class _PhpUnserializationError(ValueError):
    def __init__(self, msg, rest):
        self.message = msg
        self.rest = rest
