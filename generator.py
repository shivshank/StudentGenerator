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
    def addInfo(self, info):
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