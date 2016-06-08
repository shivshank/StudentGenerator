import random
from random import randint

class SimStudent:
    def __init__(self, id, name, age, gender, grade):
        self.id = id
        self.name = name
        self.gender = gender
        self.age = age
        self.grade = grade
        self.electives = []
        self.coreProgress = {}
        self.credits = set()
        # fails is not used
        self.fails = 0
        self.specials = []
        self.info = []
        self.enrollmentHistory = [[]]
    def attempt(self, course):
        self.enrollmentHistory[-1].append(course)
    def beginNewYear():
        self.enrollmentHistory.append([])
    def msg(self, info):
        self.info.append(info)
    def canGraduate(self):
        for course in Course.gradreqs:
            if course not in self.credits:
                return False
        return True
    def getGradReqs(self):
        reqs = []
        for course in Course.gradreqs:
            if course not in self.credits:
                reqs.append(course)
        return reqs
    def failed(self, course):
        self.fails += 1
    def passed(self, course):
        assert course not in self.credits, \
            "student took a class twice: " + course.name
        self.credits.add(course)
    def setTracks(self, **kwargs):
        for k, v in kwargs.items():
            self.coreProgress[k] = v
    def enroll(self, elective):
        self.electives.append(elective)

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
        self.nextCrn = 0
        # a dict of the form {"core class type": {"level n": [courses]}}
        self.tracks = {}
        self.all = []
        self.electives = []
        self.specials = []
        self.credits = set()
        self.gradReqs = {}
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
    def getNextCrn(self):
        res = self.nextCrn
        self.nextCrn += 1
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
        self.crn = registrar.getNextCrn()
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
    def canEnroll(self, student):
        credits = student.getCredits()
        for i in self.credits:
            if i not in credts:
                return False
        return True
    def honors(self, title=None):
        self.hasHonors = True
        self.honorsTitle = title if title is not None else self.honorsTitle
        return self
    def credit(self, *creditTypes, amt=1):
        """ Make this course credit bearing
        """
        self.worth = amt
        if len(creditTypes) > 0:
            self.reg.recordCredits(*creditTypes)
            self.credits.extend(creditTypes)
        return self
    def req(self, *reqs):
        """ Set the prerequisites for this course, by title or credit names
            reqs should be a list of course names or credit types
        """
        self.preReqs.extend(reqs)
        return self
    def track(self, track, level):
        """ Make this class part of a core track
        """
        self.reg.addCourseToTrack(self, track, level)
        return self
    def asElective(self):
        """ Register the course as an elective """
        self.reg.newElectives(self)
        return self
    def asSpecial(self):
        """ Register the course as a special """
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
Course(reg, "Band").asSpecial()
Course(reg, "Girl's PE").asSpecial()
Course(reg, "Boy's PE").asSpecial()
Course(reg, "Study Hall").asSpecial()
    # other
Course(reg, "College Success", minGrade=11).asGeneric().credit()
Course(reg, "Parenting", minGrade=12).asGeneric().credit()
reg.prettyprint()

class Course:
    all = []
    gradreqs = []
    @classmethod
    def withName(cls, name):
        for i in cls.all:
            if i.name == name:
                return i
        return None
    def __init__(self, name, hasHonors=False, grade=9):
        self.id = len(Course.all)
        self.name = name
        self.hasHonors = hasHonors
        self.grade = grade
        Course.all.append(self)
    def grad(self):
        Course.gradreqs.append(self)
        return self

simParams = {
    "girl": 0.5,
    "honors": 0.15,
    "failChance": 0.08,
    "band": 0.5,
    "dropoutAge": 17,
    "dropoutChance": 0.05,
    "maxAge": 20,
    "electives": 2,
    "enrollment": 110,
    "enrollmentMargin": 0.1,
    "lowAge": 0.4
}

Course.tracks = {
    "math": [
        Course("Algebra I"),
        Course("Geometry", True),
        Course("Algebra II").grad(),
        Course("Precalculus"),
        Course("Calculus")
    ],
    "science": [
        Course("Earth Science"),
        Course("Biology", True).grad(),
        (Course("Chemistry"), Course("Physics"))
    ],
    "history": [
        Course("Global History I", True),
        Course("Global History II", True),
        Course("American History", True).grad(),
        Course("Government").grad()
    ],
    "english": [
        Course("English I", True),
        Course("English II", True),
        Course("English III", True),
        Course("English IV", True).grad()
    ],
    "spanish": [
        Course("Spanish I", True),
        Course("Spanish II", True),
        Course("Spanish III", True).grad(),
        Course("Spanish IV", True),
        Course("Spanish V")
    ]
}

Course.electives = [
    Course("DDP"),
    Course("Intro to Electronics"),
    Course("Drawing"),
    Course("Photography"),
    Course("Ceramics"),
    Course("Intro to Programming"),
    Course("Marketing"),
    Course("Adv Biology", grade=11),
    Course("Western Civilization", grade=11),
    Course("Creative Writing", grade=11)
]

Course.specials = [
    Course("Band"),
    Course("Girl's PE"),
    Course("Boy's PE"),
    Course("Study Hall")
]

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

if __name__ == "__main__":
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