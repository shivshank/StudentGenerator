import generator

def courseSet(student, ignoreSet=None):
    if ignoreSet is None:
        return frozenset(student.getEnrolled())
    return frozenset(i for i in student.getEnrolled()
                     if i.name not in ignoreSet)

def group_bf(students, ignoreSet=None):
    """ Brute force grouping algorithm """
    # I am using the term "schedule" loosely, it's more of an "outline"
    schedules = (courseSet(i, ignoreSet) for i in students)
    # copy the first schedule to start the loop
    groups = [set(next(schedules))]
    for schedule in schedules:
        # find all schedules with which this schedule intersects/belongs
        belongs = []
        for i, g in enumerate(groups):
            # TODO: test if recording unions in place is faster
            if g & schedule:
                belongs.append(i)
        if len(belongs) == 0:
            # this student is a lone-wolf!
            groups.append(set(schedule))
            continue
        # combine all intersecting groups
        bIter = iter(belongs)
        # skip the first element
        root = groups[next(bIter)]
        root.update(schedule)
        for groupIndex in bIter:
            root.update(groups.pop(groupIndex))
            print('Joining')
    return groups

def groups_verify(students, groups, ignoreSet=None):
    for i in groups:
        for j in groups:
            if i is j:
                continue
            assert not i & j, "two groups intersected"
    schedules = (courseSet(i, ignoreSet) for i in students)
    for schedule in schedules:
        belongs = None
        for g in groups:
            if g & schedule:
                if belongs is not None:
                    print(belongs, g)
                    raise AssertionError("student belongs to multiple groups")
                else:
                    belongs = g
                    
if __name__ == "__main__":
    reg = generator.makeDefaultRegistrar(generator.gradReqs,
                                         generator.totalCredits)
    #generator.simParams["enrollment"] = 30
    students = generator.simulate(generator.simParams, reg, 4)[0]
    groups = group_bf(students, ignoreSet=["PE", "Band"])
    for i in groups:
        print("group:")
        print("\t" + "\n\t".join(map(str, i)))
    groups_verify(students, groups)
    for c in reg.all:
        if c not in groups[0]:
            print(c.name)