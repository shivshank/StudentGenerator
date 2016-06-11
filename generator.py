import random
from random import randint

simParams = {
    "lowAge": 0.6,                          # % students who enter HS at age 14
    "failChance": 0.08,                     # chance of failing a class
    "honors": 0.15,                         # chance of student getting honors
    "honorsFailChance": 0.05,               # chance of failing an honors course
    "honorsFallOut": 0.03,                  # chance of a student losing honors
    "band": 0.5,                            # percent of kids who take band
    "dropoutAge": 17,                       # age at which students can drop out
    "dropoutChance": 0.05,                  # percent of kids who drop out
    "maxAge": 20,                           # max age which students can attend
    "electives": 2,                         # electives each year
    "maxCourses": 8,                        # total courses someone can take
    "enrollment": 110,                      # baseline students enrolled
    "enrollmentMargin": 25                  # max +/- enrollment
}

gradReqs = {
    "English": 4,
    "Social Studies": 4,
    "Math": 3,
    "Science": 3,
    "PE": 4,
    "College Success": 1,
    "Art or Music": 1,
    "Tech": 0.5,
    "Spanish": 3,
    "Total": 24
}
simParams["gradReqs"] = gradReqs

randomNames = [
    "Bob", "Jack", "Dave", "John", "Cynthia", "Robert", "Ruth", "Antonin",
    "Larry", "Mike", "Sam", "Elena", "Anthony", "Clarence", "Thomas", "Kennedy",
    "Sonia", "Stephen", "Donald", "Bernard", "Henry", "Hillary", "William"
]

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
        self.enrollmentHistory = [[]]
    def beginNewYear():
        """ Record that a new year has begun (for bookkeeping only) """
        self.enrollmentHistory.append([])
    def msg(self, info):
        """ Record a message about this student (for bookkeeping only) """
        self.info.append(info)
    def enroll(self, course, asHonors=False):
        """ Record that a class was attempted """
        self.enrollmentHistory[-1].append(course)
        if asHonors:
            if not course.hasHonors:
                raise ValueError("Course", str(course), "does not have honors")
            self.asHonors.add(course)
    def isEnrolledIn(self, course):
        return course in self.enrollmentHistory[-1]
    def isEnrolledInHonors(self, course):
        if not course.hasHonors:
            return False
        return course in self.enrollmentHistory[-1] and course in self.asHonors
    def hasTaken(self, course):
        return course in self.passedClasses or course in self.failedClasses
    def getPassed(self):
        return self.passedClasses
    def failed(self, course):
        """ record that a class has been failed, receiving no credits """
        self.failedClasses.add(course)
        # discard prevents key error from being thrown for non honors courses
        self.asHonors.discard(course)
    def passed(self, course):
        """ record that a class has been passed and confer the credits """
        assert course not in self.passedClasses, \
            "student took a class twice: " + course.name
        self.passedClasses.add(course)
        # ask this course to confer its credits onto the student
        course.confer(self)
    def giveCredits(self, credits, amount):
        for i in credits:
            self.credits[i] = self.credits.get(i, 0) + amount
    def prettyprint(self):
        print(self.id, ':', *self.name, end=' ')
        print('age', str(self.age) + ', year', self.grade)
        print('\tfailed:', ', '.join(self.failedClasses))
        print('\tpassed:', ', '.join(self.passedClasses))
        print('\thonors courses:', ', '.join(self.asHonors))

def regMethod(func):
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
    @regMethod
    def newCourse(self, *args):
        """ Add a course
            This method will most likely be used for core, non elective classes.
                Record that the class is a core requirement by calling its
                "track" method.
        """
        pass
    @regMethod
    def newSpecials(self, *args):
        self.specials.extend(args)
    @regMethod
    def newElectives(self, *args):
        self.electives.extend(args)
    def addCourseToTrack(self, c, track, level):
        recordedTrack = self.tracks.setdefault(track, {})
        coursesInTrack = recordedTrack.setdefault(level, [])
        coursesInTrack.append(c)
    def getCoursesBelowLevel(self, track, level):
        """ Get the courses below (exclusive) a certain level within a track """
        reqs = []
        for l, courses in self.tracks[track].items():
            if l >= level:
                continue
            reqs.extend(courses)
        return reqs
    def getNextCourseId(self):
        res = self.nextId
        self.nextId += 1
        return res
    def recordCredits(self, *titles):
        self.credits.update(titles)
    def recordGradReqs(self, **credits):
        self.gradReqs.update(credits)
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

class Course:
    """ Contains all the information about a course, including its prerequisites
    """
    def __init__(self, registrar, name,
                 minGrade=9, hasHonors=False,  honorsTitle=None):
        self.reg = registrar
        self.id = registrar.getNextCourseId()
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
        if student.hasTaken(self):
            return False
        for i in self.preReqs:
            if not student.hasTaken(i):
                return False
        return True
    def honors(self, title=None):
        self.hasHonors = True
        self.honorsTitle = title if title is not None else self.honorsTitle
        return self
    def credit(self, *creditTypes, amt=1):
        """ Make this course credit bearing """
        self.worth = amt
        if len(creditTypes) > 0:
            self.reg.recordCredits(*creditTypes)
            self.credits.extend(creditTypes)
        return self
    def req(self, *reqs):
        """ Set the prerequisites for this course, by title or credit names
            reqs should be a list of course names or credit types
        """
        self.preReqs.extend(reg.getCourse(name=i) for i in reqs)
        return self
    def track(self, track, level):
        """ Make this class part of a core track """
        self.reg.addCourseToTrack(self, track, level)
        return self
    def asElective(self):
        """ Register the course as an elective """
        self.reg.newElectives(self)
        self.elective = True
        return self
    def asSpecial(self):
        """ Register the course as a special """
        self.special = True
        self.reg.newSpecials(self)
        return self
    def asGeneric(self):
        """ Register the course as generic """
        self.reg.newCourse(self)
        return self
    def __str__(self):
        if self.worth == 1:
            return (self.name
                   + ' (' + str(self.worth) + ' credit)')
        return (self.name
           + ' (' + str(self.worth) + ' credits)')

def trackMaker(track, credit, *courses, allHonors=True, noCredit=False):
    """ Helper method for making course tracks """
    for i, c in enumerate(courses):
        # add c as a gneric course to the track bearing credit under "credit"
        # and requiring the previous course in the track
        c.track(track, i).asGeneric()
        if not noCredit:
            c.credit(credit)
        if allHonors:
            c.honors()
        if i > 0:
            # first course has no requirements
            c.req(courses[i-1].name)

reg = Registrar()

trackMaker("Math", "Math",
    Course(reg, "Algebra I"),
    Course(reg, "Geometry"),
    Course(reg, "Algebra II"),
        allHonors=True)
Course(reg, "Precalculus").credit("Math").track("Math", 3).asGeneric() \
    .req("Algebra II")
Course(reg, "Math IV").credit("Math").track("Math", 3).asGeneric() \
    .req("Algebra II")
Course(reg, "Calculus").credit("Math").track("Math", 4) \
    .asGeneric().req("Precalculus")
trackMaker("English", "English",
    Course(reg, "English 9"),
    Course(reg, "English 10"),
    Course(reg, "English 11"),
    Course(reg, "English 12"),
        allHonors=True)
trackMaker("Social Studies", "Social Studies",
    Course(reg, "Global 9", hasHonors=True),
    Course(reg, "Global 10", hasHonors=True),
    Course(reg, "US History", hasHonors=True, honorsTitle="Adv US History"),
    Course(reg, "Government", hasHonors=False),
        allHonors=False)
trackMaker("Spanish", "Spanish",
    Course(reg, "Spanish 1", hasHonors=False),
    Course(reg, "Spanish 2", hasHonors=True),
    Course(reg, "Spanish 3", hasHonors=True),
    Course(reg, "Spanish 4", hasHonors=False),
    Course(reg, "Spanish 5", hasHonors=False),
        allHonors=False)
trackMaker("Science", "Science",
    Course(reg, "Earth Science", hasHonors=False),
    Course(reg, "Biology", hasHonors=True),
        allHonors=False)
# add the optional science courses
Course(reg, "Physics").credit("Science").track("Science", 2).asGeneric()
Course(reg, "Chemistry").credit("Science").track("Science", 2).asGeneric()

# electives
    # tech classes
Course(reg, "DDP").asElective().credit("Tech", "Art or Music")
Course(reg, "CAD/CAM").asElective().req("DDP").credit("Tech")
Course(reg, "Architecture").asElective().req("DDP").credit("Tech")
Course(reg, "Intro to Electronics").asElective().credit("Tech")
Course(reg, "Intro to Programming").asElective().credit("Tech")
Course(reg, "Intro to Web Design").asElective().credit("Tech")
    # art classes
Course(reg, "Studio in Art").asElective().credit("Art")
Course(reg, "Drawing").asElective().credit("Art").req("Studio in Art")
Course(reg, "Photography").asElective().credit("Art").req("Studio in Art")
Course(reg, "Ceramics").asElective().credit("Art").req("Studio in Art")
    # business
Course(reg, "Marketing").asElective().credit("Business")
    # liberal artsy electives
Course(reg, "Adv Biology", minGrade=11).asElective().credit()
Course(reg, "Anatomy", minGrade=11).asElective().credit()
Course(reg, "Western Civilization", minGrade=11).asElective().credit()
Course(reg, "Creative Writing", minGrade=11).asElective().credit()
    # specials
Course(reg, "Band").asSpecial().credit("Art or Music")
Course(reg, "PE").asSpecial().credit("PE")
Course(reg, "Study Hall").asSpecial()
Course(reg, "College Success", minGrade=11) \
    .asSpecial().credit("College Success")

def suggestClasses(reg, student, gradReqs,
                   ignoreElectives=True, ignoreSpecials=True):
    req = []
    options = []
    # some misc reqs might be in this list but it wont matter
    unmet = [k for k, v in gradReqs.items() if student.credits.get(k, 0) < v]
    for course in reg.all:
        if not course.canEnroll(student):
            continue
        if ignoreElectives and course.isElective():
            continue
        if ignoreSpecials and course.isSpecial():
            continue
        # if the course meets (i.e., intersects with) unmet requirements...
        if len(list(set(unmet).intersection(course.credits))) > 0:
            req.append(course)
        else:
            options.append(course)
    return req, options

def getAvailableElectives(reg, student):
    res = []
    for elective in reg.electives:
        if elective.canEnroll(student):
            res.append(elective)
    return res

def enrollNewStudent(params, reg, id):
    # generate cheasy names and student data
    age = 14 if random.random() < params["lowAge"] else 15
    lname = random.choice(randomNames) + ("s" if random.random() > 0.25 else "")
    s = Student(id, random.choice(randomNames), lname, age, 9)
    enrolledCredits = set()
    enrolledCount = 0
    req, opts = suggestClasses(reg, s, params["gradReqs"])
    # this could be a lot cleaner
    while enrolledCount < params["maxCourses"] and len(req) + len(opts) > 0:
        # TODO
        if len(req) > 0:
            selected = req.pop(randint(0, len(req)-1))
            enrolledCredits.update(selected.credits)
            enrolledCount += 1
        if len(opts) > 0:
            selected = opts.pop(randint(0, len(opts)-1))
            enrolledCount += 1
            enrolledCredits.update(selected.credits)
    return s

enrollNewStudent(simParams, reg, 7)

def enrollYear(studentsList, params):
    # the first parameter is an out parameter to be more consistent with
    # advanceStudents
    students = []
    margin = (random.random() * 2 - 1) * params["enrollmentMargin"] * \
              params["enrollment"]
    enrolled = params["enrollment"] + int(round(margin, 0))
    trackProgress = lambda: (
        (1, True) if random.random() > params["honors"] else (0, False))
    for i in range(enrolled):
        gender = "girl" if random.random() <= params["girl"] else "boy"
        age = 14 if random.random() <= params["lowAge"] else 15
        s = SimStudent(i, "", age, gender, 9)
        s.setTracks(
            math=trackProgress(),
            science=trackProgress(),
            history=trackProgress(),
            english=trackProgress(),
            spanish=trackProgress())
        students.append(s)
    studentsList.extend(students)
    return enrolled

def advanceStudents(students, params):
    dropouts = []
    graduates = []
    for s in students:
        # set specials
        s.specials = []
        if random.random() <= params["band"]:
            s.specials.append(Course.withName("Band"))
        # check if they passed or failed their electives
        for elective in s.electives:
            if random.random() <= params["failChance"]:
                s.failed(elective)
            else:
                s.passed(elective)
        # figure out what electives they are taking now
        s.electives = []
        for i in range(params["electives"]):
            # a student can only take electives they haven't passed and
            # that they haven't taken yet
            available = [i for i in Course.electives 
                         if i.grade <= s.grade and i not in s.credits
                                               and i not in s.electives]
            if len(available) == 0:
                # student has taken or will have taken every elective
                break
            chosen = random.choice(available)
            s.enroll(chosen)
        # advance their core progress
        for track, progress in s.coreProgress.items():
            if progress[0] == None:
                # None marks that the track is complete
                continue
            if random.random() <= params["failChance"]:
                s.failed(Course.tracks[track][progress[0]])
            else:
                s.passed(Course.tracks[track][progress[0]])
                if progress[0] + 1< len(Course.tracks[track]):
                    s.coreProgress[track] = (progress[0] + 1, progress[1])
                else:
                    s.coreProgress[track] = (None, progress[1])
        # update rolling stats
        s.age += 1
        if s.grade < 12:
            s.grade += 1
        # check if student graduated dropped out
        if s.canGraduate():
            graduates.append(s)
        elif s.age > params["maxAge"]:
            dropouts.append(s)
        elif s.age > params["dropoutAge"] \
             and random.random() <= params["dropoutChance"]:
            dropouts.append(s)
    for s in dropouts:
        students.remove(s)
    for s in graduates:
        students.remove(s)
    return dropouts, graduates

def simulate(params, years=4, enrollingYears=None):
    # simulate four years of school
    students = []
    dropouts = []
    graduates = []
    enrolled = 0
    enrollingYears = years if enrollingYears is None else enrollingYears
    for i in range(years):
        dropped, grads = advanceStudents(students, params)
        dropouts.extend(dropped)
        graduates.extend(grads)
        if enrollingYears > 0:
            enrolled += enrollYear(students, params)
            enrollingYears -= 1
    return enrolled, students, dropouts, graduates

if __name__ == "__main__z":
    enrolled, students, dropouts, graduates = simulate(simParams, 8, 1)
    print('total enrolled', enrolled)
    print('dropouts', len(dropouts))
    print('grads', len(graduates))
    for i in students:
        print([j.name for j in i.getGradReqs()])
    avgGradAge = sum(s.age for s in graduates)/len(graduates)
    print('Average age of graduate:', avgGradAge)
    print('Graduates aged 19:', len([i for i in graduates if i.age == 19]) )
    print('Graduates aged 18:', len([i for i in graduates if i.age == 18]))
    print('Graduates aged 17:', len([i for i in graduates if i.age == 17]))