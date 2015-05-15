# The contents of this file need to be pasted into the loncapa/python
# script tag of the problem XML definition - see api-example.xml for
# an example.

import json
import math

def vglcfn(e, ans):
    """Main grading function."""
    try:
        custom_checks
    except NameError:
        custom_checks = {}
    try:
        success_message
    except NameError:
        success_message = 'Good job!'

    answer = json.loads(json.loads(ans)['answer'])
    grader = Grader(answer, custom_checks, success_message)
    return grader.grade()


## Built-in check functions

def check_presence(check, vectors):
    if check['vector'] not in vectors:
        return 'You need to use the {} vector.'.format(check['vector'])

def check_tail(check, vectors):
    vec = vectors[check['vector']]
    tolerance = check.get('tolerance', 1.0)
    expected = check['expected']
    dist = math.hypot(expected[0] - vec.tail.x, expected[1] - vec.tail.y)
    if dist > tolerance:
        return 'Vector {} does not start at correct point.'.format(vec.name)

def check_tip(check, vectors):
    vec = vectors[check['vector']]
    tolerance = check.get('tolerance', 1.0)
    expected = check['expected']
    dist = math.hypot(expected[0] - vec.tip.x, expected[1] - vec.tip.y)
    if dist > tolerance:
        return 'Vector {} does not end at correct point.'.format(vec.name)

def _check_coordinate(check, coord):
    tolerance = check.get('tolerance', 1.0)
    expected = check['expected']
    return abs(expected - coord) > tolerance

def check_tail_x(check, vectors):
    vec = vectors[check['vector']]
    if _check_coordinate(check, vec.tail.x):
        return 'Vector {} does not start at correct point.'.format(vec.name)

def check_tail_y(check, vectors):
    vec = vectors[check['vector']]
    if _check_coordinate(check, vec.tail.y):
        return 'Vector {} does not start at correct point.'.format(vec.name)

def check_tip_x(check, vectors):
    vec = vectors[check['vector']]
    if _check_coordinate(check, vec.tip.x):
        return 'Vector {} does not end at correct point.'.format(vec.name)

def check_tip_y(check, vectors):
    vec = vectors[check['vector']]
    if _check_coordinate(check, vec.tip.y):
        return 'Vector {} does not end at correct point.'.format(vec.name)

def _check_coords(vec, expected, tolerance):
    for expected_coords, vec_coords in ([expected[0], vec.tail], [expected[1], vec.tip]):
        if expected_coords[0] == '_':
            if expected_coords[1] != '_':
                # Only y given; not interested in x.
                if abs(expected_coords[1] - vec_coords.y) > tolerance:
                    return True
        elif expected_coords[1] == '_':
            # Only x given; not interested in y.
            if abs(expected_coords[0] - vec_coords.x) > tolerance:
                return True
        else:
            # Both coordinates given; check distance from expected point.
            x = expected_coords[0] - vec_coords.x
            y = expected_coords[1] - vec_coords.y
            if math.hypot(x, y) > tolerance:
                return True
    return False

def check_coords(check, vectors):
    vec = vectors[check['vector']]
    expected = check['expected']
    tolerance = check.get('tolerance', 1.0)
    if _check_coords(vec, expected, tolerance):
        return 'Vector {} coordinates are not correct.'.format(vec.name)

def check_segment_coords(check, vectors):
    vec = vectors[check['vector']]
    expected = check['expected']
    tolerance = check.get('tolerance', 1.0)
    if _check_coords(vec, expected, tolerance) and \
            _check_coords(vec.opposite(), expected, tolerance):
        return 'Segment {} coordinates are not correct.'.format(vec.name)

def check_length(check, vectors):
    vec = vectors[check['vector']]
    tolerance = check.get('tolerance', 1.0)
    if abs(vec.length - check['expected']) > tolerance:
        return 'The length of {} is incorrect. Your length: {:.1f}'.format(vec.name, vec.length)

def _check_angle(vec, expected, tolerance):
    # Calculate angle between vec and identity vector with expected angle
    # using the formula:
    # angle = acos((A . B) / len(A)*len(B))
    x = vec.tip.x - vec.tail.x
    y = vec.tip.y - vec.tail.y
    dot_product = x * math.cos(expected) + y * math.sin(expected)
    angle = math.degrees(math.acos(dot_product / vec.length))
    return abs(angle) > tolerance

def check_angle(check, vectors):
    vec = vectors[check['vector']]
    tolerance = check.get('tolerance', 2.0)
    expected = math.radians(check['expected'])
    if _check_angle(vec, expected, tolerance):
        return 'The angle of {} is incorrect. Your angle: {:.1f}'.format(vec.name, vec.angle)

def check_segment_angle(check, vectors):
    # Segments are not directed, so we must check the angle between the segment and
    # the vector that represents it, as well as its opposite vector.
    vec = vectors[check['vector']]
    tolerance = check.get('tolerance', 2.0)
    expected = math.radians(check['expected'])
    if _check_angle(vec, expected, tolerance):
        if _check_angle(vec.opposite(), expected, tolerance):
            return 'The angle of {} is incorrect. Your angle: {:.1f}'.format(vec.name, vec.angle)


class Point(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Vector(object):
    def __init__(self, name, x1, y1, x2, y2):
        self.name = name
        self.tail = Point(x1, y1)
        self.tip = Point(x2, y2)
        self.length = math.hypot(x2 - x1, y2 - y1)
        angle = math.degrees(math.atan2(y2 - y1, x2 - x1))
        if angle < 0:
            angle += 360
        self.angle = angle

    def opposite(self):
        return Vector(self.name, -self.tail.x, -self.tail.y, -self.tip.x, -self.tip.y)

class Grader(object):
    check_registry = {
        'presence': check_presence,
        'tail': check_tail,
        'tip': check_tip,
        'tail_x': check_tail_x,
        'tail_y': check_tail_y,
        'tip_x': check_tip_x,
        'tip_y': check_tip_y,
        'coords': check_coords,
        'length': check_length,
        'angle': check_angle,
        'segment_angle': check_segment_angle,
        'segment_coords': check_segment_coords,
    }

    def __init__(self, answer, custom_checks, success_message='Test passed'):
        self.answer = answer
        self.check_registry.update(custom_checks)
        self.success_message = success_message

    def grade(self):
        for check in self.answer['checks']:
            check_fn = self.check_registry[check['check']]
            result = check_fn(check, self._get_vectors())
            if result:
                return {'ok': False, 'msg': result}

        return {'ok': True, 'msg': self.success_message}

    def _get_vectors(self):
        vectors = {}
        for name, props in self.answer['vectors'].iteritems():
            tail = props['tail']
            tip = props['tip']
            vectors[name] = Vector(name, tail[0], tail[1], tip[0], tip[1])
        return vectors
