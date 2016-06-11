import random
from random import randint
import model
from model import Registrar, Student

class Course(model.Course):
    """ An extension of Course for easier in-code Course definitions """
    def __init__(self, registrar, name, **kwargs):
        super().__init__(registrar.getNextCourseId(), name, **kwargs)
        self.reg = registrar
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
        self.preReqs.extend(self.reg.getCourse(name=i) for i in reqs)
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

simParams = {
    "lowAge": 0.6,                          # % students who enter HS at age 14
    "failChance": 0.08,                     # chance of failing a class
    "honors": 0.17,                         # chance of student getting honors
    # how much more likely an honors student is to have more honors classes
    "honorsCompound": 0.3,
    "honorsFailChance": 0.03,               # chance of failing an honors course
    "honorsFallOut": 0.06,                  # chance of a student losing honors
    "band": 0.5,                            # percent of kids who take band
    "dropoutAge": 17,                       # age at which students can drop out
    "dropoutChance": 0.03,                  # percent of kids who drop out
    "maxAge": 20,                           # max age which students can attend
    "electives": 2,                         # electives each year
    "maxCourses": 8,                        # total courses someone can take
    "enrollment": 110,                      # baseline students enrolled
    "enrollmentMargin": 25,                 # max +/- enrollment
    # freshman can start already having credit in these courses
    "skippable": {"Earth Science", "Algebra I"}
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
    "Spanish": 3
}
totalCredits = 24

randomNames = [
    "Bob", "Jack", "Dave", "John", "Cynthia", "Robert", "Ruth", "Antonin",
    "Larry", "Mike", "Sam", "Elena", "Anthony", "Clarence", "Thomas", "Kennedy",
    "Sonia", "Stephen", "Donald", "Bernard", "Henry", "Hillary", "William"
]

def makeDefaultRegistrar(gradReqs):
    reg = Registrar()

    trackMaker("Math", "Math",
        Course(reg, "Algebra I", hasHonors=False),
        Course(reg, "Geometry", hasHonors=True),
        Course(reg, "Algebra II", hasHonors=True),
            allHonors=False)
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
    Course(reg, "Physics").credit("Science").track("Science", 2) \
        .asGeneric().req("Earth Science", "Biology")
    Course(reg, "Chemistry").credit("Science").track("Science", 2) \
        .asGeneric().req("Earth Science", "Biology")
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
    reg.recordGradReqs(**gradReqs)
    return reg

def suggestClasses(reg, student, ignoreElectives=True, ignoreSpecials=True):
    req = []
    options = []
    for course in reg.all:
        if not course.canEnroll(student):
            continue
        if ignoreSpecials and course.isSpecial():
            continue
        if ignoreElectives and course.isElective():
            continue
        elif course.isElective():
            options.append(course)
            continue
        # if the course meets (i.e., intersects with) unmet requirements...
        if isTowardProgress(reg, course, student):
            req.append(course)
        else:
            options.append(course)
    return req, options

def isTowardProgress(reg, course, student):
    gradReqs = reg.gradReqs
    # get all credit categories from gradReqs that are unfulfilled by student
    unmet = [k for k, v in gradReqs.items()
             if student.getCredits().get(k, 0) < v]
    return len(set(unmet).intersection(course.credits)) > 0

def getAvailableElectives(reg, student):
    res = []
    for elective in reg.electives:
        if elective.canEnroll(student):
            res.append(elective)
    return res

def enrollNewStudent(params, reg, id):
    """ Generate a new 9th grade Freshman """
    # generate cheasy names and student data
    skippable = params["skippable"]
    age = 14 if random.random() < params["lowAge"] else 15
    lname = random.choice(randomNames) + ("s" if random.random() > 0.25 else "")
    s = Student(id, random.choice(randomNames), lname, age, 9)
    s.beginNewYear()
    s.enroll(reg.getCourse(name="PE"))
    enrolledCount = 1
    if random.random() < params["band"]:
        s.enroll(reg.getCourse(name="Band"))
        enrolledCount += 1
    req, opts = suggestClasses(reg, s, ignoreElectives=False)
    honorsChance = params["honors"]
    def asHonors(c):
        nonlocal honorsChance
        res = c.hasHonors and random.random() < honorsChance
        if res:
            honorsChance *= 1 + params["honorsCompound"]
        return res
    while enrolledCount < params["maxCourses"] and len(req) > 0:
        selected = req.pop(randint(0, len(req)-1))
        if selected.name in skippable:
            honorsResult = random.random() < honorsChance
            honorsChance *= (1 + params["honorsCompound"])**honorsResult
            if honorsResult:
                # give student credit for the course
                s.passed(selected, True, overrideHonors=True)
                selected = next(i for i in reg.getCoursesRequiring(selected)
                                if i.canEnroll(s))
                # enroll them in the next course
                s.enroll(selected, random.random() >= params["honorsFallOut"])
                enrolledCount += 1
                continue
        honorsResult = asHonors(selected)
        s.enroll(selected, honorsResult)
        enrolledCount += 1
    while enrolledCount < params["maxCourses"] and len(opts) > 0:
        selected = opts.pop(randint(0, len(opts)-1))
        # electives probably won't have honors versions, but just in case
        s.enroll(selected, asHonors(selected))
        enrolledCount += 1
    return s

def enrollYear(params, reg, baseId):
    students = []
    margin = (random.random() * 2 - 1) * params["enrollmentMargin"]
    enrolled = params["enrollment"] + int(round(margin, 0))
    for i in range(enrolled):
        students.append(enrollNewStudent(params, reg, i + baseId))
    return students

def advanceStudent(params, reg, student):
    # resolve this students classes
    honorsChance = params["honorsChance"] * \
                   (1 + params["honorsCompound"])**len(student.asHonors)
    def asHonors(c):
        res = c.hasHonors and random.random() < honorsChance
        honorsChance *= 1 if not res else (1 + params["honorsCompound"])
        return res
    for course in student.getEnrolled():
        if course in student.asHonors:
            # TODO: is this the right way to do random chances for this case?
            if random.random() < params["honorsFailChance"]:
                # student failed the honors class
                student.failed(course)
            elif random.random() < params["honorsFallOut"]:
                # student passed but without honors
                student.passsed(course, False)
            else:
                # student passed with honors
                student.passed(course, True)
            continue
        if random.random() < params["failChance"]:
            student.failed(course)
        else:
            student.passed(course)
    student.beginNewYear()
    student.enroll(reg.getCourse(name="PE"))
    enrolled = 1
    if random.random() < params["band"]:
        student.enroll(reg.getCourse(name="Band"))
        enrolled += 1
    if s.grade >= 11:
        # prioritize required classes after junior year
        maxReqs = params["maxCourses"]
    else:
        maxReqs = params["maxCourses"] - params["electives"]
    req, opts = suggestClasses(reg, s, ignoreElectives=False)
    while enrolled < maxReqs and len(req) > 0:
        selected = req.pop(randint(0, len(req)-1))
        student.enroll(selected, asHonors(selected))
        enrolled += 1
    while enrolled < params["maxCourses"] and len(opts) > 0:
        selected = opts.pop(randint(0, len(opts)-1))
        student.enroll(selected, asHonors(selected))
        enrolled += 1

def advanceStudents(params, reg, students):
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

def simulate(params, reg, years=4, enrollingYears=None):
    # simulate four years of school
    students = []
    dropouts = []
    graduates = []
    enrolled = 0
    enrollingYears = years if enrollingYears is None else enrollingYears
    for i in range(years):
        dropped, grads = advanceStudents(params, reg, students)
        dropouts.extend(dropped)
        graduates.extend(grads)
        if enrollingYears > 0:
            newStudents = enrollYear(params, reg, len(students))
            enrolled += len(newStudents)
            students.extend(newStudents)
            enrollingYears -= 1
    return students, enrolled, dropouts, graduates

if __name__ == "__main__":
    reg = makeDefaultRegistrar(gradReqs)
    students, enrolled, dropouts, graduates = simulate(simParams, reg, 1, 1)
    
    """
    print('total enrolled', enrolled)
    print('dropouts', len(dropouts))
    print('grads', len(graduates))
    for i in students:
        print([j.name for j in i.getGradReqs()])
    avgGradAge = sum(s.age for s in graduates)/len(graduates)
    print('Average age of graduate:', avgGradAge)
    print('Graduates aged 19:', len([i for i in graduates if i.age == 19]) )
    print('Graduates aged 18:', len([i for i in graduates if i.age == 18]))
    print('Graduates aged 17:', len([i for i in graduates if i.age == 17]))"""