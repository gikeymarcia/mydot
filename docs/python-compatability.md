# Python Compatability

Attempting to track which features of Python I'm using that effect compatability.

## In Use

### Python 3.5 +

- Extensive use of type hinting and imports from the `typing` module in the 
  standard library.

### Python 3.6 +

- Formatted string literals a.k.a [f-strings][f-strings]
- Type hints [for variables][var annotation]

### Python 3.8 +

- Assignment expressions a.ka. [the walrus operator][walrus]
- Using the `@cached_property` decorator from [`functools`][cached prop]

### Python 3.10 +

- Structural pattern matching (`match`/`case`) via [PEP 634][match]
- Union type syntax `X | Y` via [PEP 604][union] (used in some places, `typing.Union` still present in others)

[match]: <https://www.python.org/dev/peps/pep-0634/>
"PEP 634 -- Structural Pattern Matching"

[union]: <https://www.python.org/dev/peps/pep-0604/>
"PEP 604 -- Allow writing union types as X | Y"
[f-strings]: <https://www.python.org/dev/peps/pep-0498/>
"PEP 498 -- Liter String Interpolation"
[walrus]: <https://www.python.org/dev/peps/pep-0572/>
"PEP 572 -- Assignment Expressions"
[var annotation]: <https://www.python.org/dev/peps/pep-0526/>
"PEP 526 -- Syntax for Variable Assignment"
[cached prop]: <https://docs.python.org/3/library/functools.html#functools.cached_property>
"functools -- Higher-order functions and operations on callable objects"
