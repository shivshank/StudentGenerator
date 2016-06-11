def _regMethod(func):
    """ Decorate Registrar methods so that they perform standard book keeping
        operations
    """
    def wrap(*args):
        args[0].all.extend(args[1:])
        func(*args)
    return wrap

class Registrar:
    """ Contains information relevant to finding courses
        Should avoid duplicating information that can be gleaned from searching
            the courses contained within.
    """
    def __init__(self):
        self.nextId = 0
        # a dict of the form {"core class type": {"level n": [courses]}}
        self.tracks = {}
        self.all = []
        self.electives = []
        self.specials = []
        self.credits = set()
        self.gradReqs = {}
        self.gradCredits = 0
    def getCourse(self, id=None, name=None):
        if id is not None:
            return self.getCourseById(id)
        if name is not None:
            return self.getCourseByName(name)
        return None
    def getCourseByName(self, name):
        for i in self.all:
            if i.name == name:
                return i
        return None
    def getCourseById(self, id):
        # see if the course is at that index
        try:
            res = self.all[id]
            if res.id == id:
                return res
        except IndexError:
            pass
        for i in self.all:
            if i.id == id:
                return i
        return None
    @_regMethod
    def newCourse(self, *args):
        """ Add a course
            This method will most likely be used for core, non elective classes.
                Record that the class is a core requirement by calling its
                "track" method.
        """
        pass
    @_regMethod
    def newSpecials(self, *args):
        self.specials.extend(args)
    @_regMethod
    def newElectives(self, *args):
        self.electives.extend(args)
    def addCourseToTrack(self, c, track, level):
        recordedTrack = self.tracks.setdefault(track, {})
        coursesInTrack = recordedTrack.setdefault(level, [])
        coursesInTrack.append(c)
    def getCoursesAfterLevel(self, track, level):
        """ Get succeeding courses in a track, including the level - course """
        reqs = []
        for l, courses in self.tracks[track].items():
            if l > level:
                continue
            reqs.extend(courses)
        return reqs
    def getCoursesBelowLevel(self, track, level):
        """ Get the courses below (exclusive) a certain level within a track """
        reqs = []
        for l, courses in self.tracks[track].items():
            if l >= level:
                continue
            reqs.extend(courses)
        return reqs
    def getCoursesRequiring(self, req):
        return [course for course in self.all if course.hasPrerequisite(req)]
    def getNextCourseId(self):
        res = self.nextId
        self.nextId += 1
        return res
    def recordCredits(self, *titles):
        """ Record that titles are a type of credit """
        self.credits.update(titles)
    def recordGradReqs(self, totalReq, **credits):
        self.gradReqs.update(credits)
        self.totalReq = totalReq
    def canGraduate(self, student):
        earned = student.getCredits()
        for creditTitle, amount in self.gradReqs.items():
            if earned.get(creditTitle, 0) < amount:
                return False
        return True
    def getMissingReqs(self, student):
        earned = student.getCredits()
        missing = {}
        for creditTitle, amount in self.gradReqs.items():
            has = earned.get(creditTitle, 0)
            if has < amount:
                missing[creditTitle] = amount - has
        return missing
    def prettyprint(self):
        # this method makes me cringe a little bit
        print('Registry:')
        print('  Total Courses (discluding honors):', len(self.all))
        # keep track of listed so we can see what courses are not in a track,
        # special, or elective
        listed = []
        print('  Tracks:')
        for track, levels in self.tracks.items():
            print('  '*2, track)
            for level in levels.values():
                for course in level:
                    print(self._prettyprintCourse(3, course))
                    listed.append(course)
        print('  Electives:')
        for i in self.electives:
            print(self._prettyprintCourse(2, i))
            listed.append(i)
        print('  Specials:')
        for i in self.specials:
            print(self._prettyprintCourse(2, i))
            listed.append(i)
        print('  Other:')
        for i in self.all:
            if i not in listed:
                print(self._prettyprintCourse(2, i))
        print('-END-')
    def _prettyprintCourse(self, indent, c):
        base = '   '*indent + str(c)
        if c.hasHonors:
            base += '\tw/ HON ' + c.honorsTitle
        return base

class Student:
    def __init__(self, id, fname, lname, age, grade):
        self.id = id
        self.name = (fname, lname)
        self.age = age
        self.grade = grade
        self.info = []
        # classes passed and failed
        self.failedClasses = set()
        self.passedClasses = set()
        # asHonors is used to see if a student is taking/passed an honors class
        self.asHonors = set()
        # represents credits earned
        self.credits = {}
        # each year is represented by a list of courses
        self.enrollmentHistory = []
    def beginNewYear(self):
        """ Record that a new year has begun (for bookkeeping only) """
        self.enrollmentHistory.append([])
    def msg(self, info):
        """ Record a message about this student (for bookkeeping only) """
        self.info.append(info)
    def enroll(self, course, asHonors=False, allowRetake=False):
        """ Record that a class was attempted """
        if len(self.enrollmentHistory) < 1:
            raise IndexError("You must call beginNewYear before enrolling")
        if allowRetake and course in self.passedClasses:
            self.passedClasses.remove(course)
        self.enrollmentHistory[-1].append(course)
        if asHonors:
            if not course.hasHonors:
                raise ValueError("Course", str(course), "does not have honors")
            self.asHonors.add(course)
    def getEnrolled(self):
        return self.enrollmentHistory[-1]
    def isEnrolledIn(self, course):
        return course in self.enrollmentHistory[-1]
    def isEnrolledInHonors(self, course):
        return course in self.enrollmentHistory[-1] and course in self.asHonors
    def hasTaken(self, course):
        return course in self.passedClasses or course in self.failedClasses
    def hasPassed(self, course):
        return course in self.passedClasses
    def getPassed(self):
        return self.passedClasses
    def getCredits(self):
        return self.credits
    def failed(self, course):
        """ record that a class has been failed, receiving no credits """
        if course in self.passedClasses:
            raise ValueError("student has already passed " + str(course))
        self.failedClasses.add(course)
        # discard prevents key error from being thrown for non honors courses
        self.asHonors.discard(course)
    def passed(self, course, asHonors, overrideHonors=False):
        """ record that a class has been passed and confer the credits """
        if course in self.passedClasses:
            raise ValueError("student has already passed " + str(course))
        if asHonors:
            if overrideHonors:
                self.asHonors.add(course)
            elif course not in self.asHonors:
                raise ValueError("student has already passed " + str(course))
        else:
            # the student did not pass with honors credits
            self.asHonors.discard(course)
        self.passedClasses.add(course)
        # ask this course to confer its credits onto the student
        course.confer(self)
    def giveCredits(self, credits, amount):
        for i in credits:
            self.credits[i] = self.credits.get(i, 0) + amount
    def prettyprint(self):
        print(self.id, ':', *self.name, end=', ')
        print('age', str(self.age) + ', year', self.grade)
        print('\tfailed:')
        print('\t\t', ', '.join(i.name for i in self.failedClasses))
        print('\tpassed:')
        print('\t\t', ', '.join(i.name for i in self.passedClasses))
        print('\thonors courses:', ', '.join(i.name for i in self.asHonors))
        print('\tenrolled:', end='\n\t\t')
        print('\n\t\t'.join(str(i) for i in self.enrollmentHistory[-1]))
        print()
        
class Course:
    """ Contains all the information about a course, including its prerequisites
    """
    def __init__(self, id, name,
                 minGrade=9, hasHonors=False, honorsTitle=None):
        self.id = id
        self.name = name
        # record if this course has an honors equivalent
        self.hasHonors = hasHonors
        self.honorsTitle = name if honorsTitle is None else honorsTitle
        self.grade = minGrade
        # how many credits this course confers
        self.worth = 0
        # a list of the credit categories for this course
        self.credits = []
        # the credits required to enroll in this course
        self.preReqs = []
        self.elective = False
        self.special = False
    def confer(self, student):
        student.giveCredits(self.credits, self.worth)
    def isElective(self):
        return self.elective
    def isSpecial(self):
        return self.special
    def canEnroll(self, student):
        if student.grade < self.grade:
            return False
        # don't let a student take a class twice
        if student.hasPassed(self):
            return False
        for i in self.preReqs:
            if not student.hasTaken(i):
                return False
        return True
    def hasPrerequisite(self, course):
        return course in self.preReqs
    def __str__(self):
        name = self.name
        if self.worth == 1:
            return name + ' (' + str(self.worth) + ' credit)'
        return name + ' (' + str(self.worth) + ' credits)'

