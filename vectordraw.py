# Please recreate pyton_lib.zip after you modify this file:
#   zip python_lib.zip vectordraw.py

###################
### Python API ####
###################

import json
import math


## Built-in check functions

def _errmsg(default_message, check, vectors):
    template = check.get('errmsg', default_message)
    vec = vectors[check['vector']]
    return template.format(name=vec.name,
                           tail_x=vec.tail.x,
                           tail_y=vec.tail.y,
                           tip_x=vec.tip.x,
                           tip_y=vec.tip.y,
                           length=vec.length,
                           angle=vec.angle)

def check_presence(check, vectors):
    if check['vector'] not in vectors:
        errmsg = check.get('errmsg', 'You need to use the {name} vector.')
        return errmsg.format(name=check['vector'])

def check_tail(check, vectors):
    vec = vectors[check['vector']]
    tolerance = check.get('tolerance', 1.0)
    expected = check['expected']
    dist = math.hypot(expected[0] - vec.tail.x, expected[1] - vec.tail.y)
    if dist > tolerance:
        return _errmsg('Vector {name} does not start at correct point.', check, vectors)

def check_tip(check, vectors):
    vec = vectors[check['vector']]
    tolerance = check.get('tolerance', 1.0)
    expected = check['expected']
    dist = math.hypot(expected[0] - vec.tip.x, expected[1] - vec.tip.y)
    if dist > tolerance:
        return _errmsg('Vector {name} does not end at correct point.', check, vectors)

def _check_coordinate(check, coord):
    tolerance = check.get('tolerance', 1.0)
    expected = check['expected']
    return abs(expected - coord) > tolerance

def check_tail_x(check, vectors):
    vec = vectors[check['vector']]
    if _check_coordinate(check, vec.tail.x):
        return _errmsg('Vector {name} does not start at correct point.', check, vectors)

def check_tail_y(check, vectors):
    vec = vectors[check['vector']]
    if _check_coordinate(check, vec.tail.y):
        return _errmsg('Vector {name} does not start at correct point.', check, vectors)

def check_tip_x(check, vectors):
    vec = vectors[check['vector']]
    if _check_coordinate(check, vec.tip.x):
        return _errmsg('Vector {name} does not end at correct point.', check, vectors)

def check_tip_y(check, vectors):
    vec = vectors[check['vector']]
    if _check_coordinate(check, vec.tip.y):
        return _errmsg('Vector {name} does not end at correct point.', check, vectors)

def _coord_delta(expected, actual):
    if expected == '_':
        return 0
    else:
        return expected - actual

def _coords_within_tolerance(vec, expected, tolerance):
    for expected_coords, vec_coords in ([expected[0], vec.tail], [expected[1], vec.tip]):
        delta_x = _coord_delta(expected_coords[0], vec_coords.x)
        delta_y = _coord_delta(expected_coords[1], vec_coords.y)
        if math.hypot(delta_x, delta_y) > tolerance:
            return False
    return True

def check_coords(check, vectors):
    vec = vectors[check['vector']]
    expected = check['expected']
    tolerance = check.get('tolerance', 1.0)
    if not _coords_within_tolerance(vec, expected, tolerance):
        return _errmsg('Vector {name} coordinates are not correct.', check, vectors)

def check_segment_coords(check, vectors):
    vec = vectors[check['vector']]
    expected = check['expected']
    tolerance = check.get('tolerance', 1.0)
    if not (_coords_within_tolerance(vec, expected, tolerance) or
            _coords_within_tolerance(vec.opposite(), expected, tolerance)):
        return _errmsg('Segment {name} coordinates are not correct.', check, vectors)

def check_length(check, vectors):
    vec = vectors[check['vector']]
    tolerance = check.get('tolerance', 1.0)
    if abs(vec.length - check['expected']) > tolerance:
        return _errmsg('The length of {name} is incorrect. Your length: {length:.1f}', check, vectors)

def _angle_within_tolerance(vec, expected, tolerance):
    # Calculate angle between vec and identity vector with expected angle
    # using the formula:
    # angle = acos((A . B) / len(A)*len(B))
    x = vec.tip.x - vec.tail.x
    y = vec.tip.y - vec.tail.y
    dot_product = x * math.cos(expected) + y * math.sin(expected)
    angle = math.degrees(math.acos(dot_product / vec.length))
    return abs(angle) <= tolerance

def check_angle(check, vectors):
    vec = vectors[check['vector']]
    tolerance = check.get('tolerance', 2.0)
    expected = math.radians(check['expected'])
    if not _angle_within_tolerance(vec, expected, tolerance):
        return _errmsg('The angle of {name} is incorrect. Your angle: {angle:.1f}', check, vectors)

def check_segment_angle(check, vectors):
    # Segments are not directed, so we must check the angle between the segment and
    # the vector that represents it, as well as its opposite vector.
    vec = vectors[check['vector']]
    tolerance = check.get('tolerance', 2.0)
    expected = math.radians(check['expected'])
    if not (_angle_within_tolerance(vec, expected, tolerance) or
            _angle_within_tolerance(vec.opposite(), expected, tolerance)):
        return _errmsg('The angle of {name} is incorrect. Your angle: {angle:.1f}', check, vectors)

def _min_dist_within_tolerance(vec,point,tolerance):
    #Determine line through endpoints of vector
    #calculate minimum 2D-distance from point to line, and check if less than tolerance
    slope = (vec.tip.y-vec.tail.y)/(vec.tip.x-vec.tail.x)
    y_intercept = vec.tail.y - slope*vec.tail.x
    min_dist = abs(slope*point.x-point.y+y_intercept)/math.sqrt(1+slope**2)
    return min_dist < tolerance

def check_through(check,vectors):
    vec = vectors[check['vector']]
    tolerance = check.get('tolerance', 1.0)
    points = check.get('expected')
    for point in points:
        point = Point(point[0],point[1])
        if not _min_dist_within_tolerance(vec,point,tolerance):
            return _errmsg('The line {name} does not pass through the correct points.', check, vectors)

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
        return Vector(self.name, self.tip.x, self.tip.y, self.tail.x, self.tail.y)

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
        'through':check_through
    }

    def __init__(self, success_message='Test passed', custom_checks=None):
        self.success_message = success_message
        if custom_checks:
            self.check_registry.update(custom_checks)

    def grade(self, answer):
        for check in answer['checks']:
            check_fn = self.check_registry[check['check']]
            result = check_fn(check, self._get_vectors(answer))
            if result:
                return {'ok': False, 'msg': result}
        return {'ok': True, 'msg': self.success_message}

    def cfn(self, e, ans):
        answer = json.loads(json.loads(ans)['answer'])
        return self.grade(answer)

    def _get_vectors(self, answer):
        vectors = {}
        for name, props in answer['vectors'].iteritems():
            tail = props['tail']
            tip = props['tip']
            vectors[name] = Vector(name, tail[0], tail[1], tip[0], tip[1])
        return vectors
