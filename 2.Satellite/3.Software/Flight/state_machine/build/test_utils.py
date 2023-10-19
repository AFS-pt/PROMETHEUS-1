try:
    from ulab import numpy
except ImportError:
    import numpy

norm = numpy.linalg.norm

less_in_magnitude = (
    lambda vec, magnitude: norm(vec) < magnitude,
    "less in magnitude than"
)

greater_in_magnitude = (
    lambda vec, magnitude: norm(vec) > magnitude,
    "greater in magnitude than"
)

def _between(v, r):
    (a, b) = r
    return a <= v <= b


between = (
    _between,
    "between the values"
)

def vec_approx_equal_generator(threshold):
    return (
        lambda vec, magnitude: norm(vec - magnitude) < threshold,
        f"approximately equal within a threshold of {threshold} to"
    )

def vec_different_generator(threshold):
    return (
        lambda vec, magnitude: norm(vec - magnitude) > threshold,
        f"different by atleast {threshold} when compared to"
    )

def cleanup_reading(reading):
    try:
        return tuple(reading)
    except Exception:
        return reading

def expect(reading, condition, expected):
    """Expect reading to satisfy condition(reading, expected).
    Returns a tuple containing a description string and a boolean indicating sucess

    :param reading: The reading to test
    :param condition: A tuple containing a function and a string describing the condition
    :type condition: (function, string)
    :param expected: The expected value
    """
    (operator, op_desc) = condition
    if operator(reading, expected):
        return (f"{cleanup_reading(reading)} is {op_desc} {expected}", True)
    else:
        return (f"{cleanup_reading(reading)} is not {op_desc} {expected}", False)
