import calendize
import info



vals = info.main()
for i in range(len(vals)):
    for j in range(len(vals[i][1])):
        course = vals[i][0]
        name = vals[i][1][j]
        dateline = vals[i][2][j]
        year = dateline[:4]
        month = dateline[5:7]
        day = dateline[8:10]
        if calendize.calendize(course, name, month, day, year):
            print("Addition of "+str(name)+" from course " + str(course) + " successful.")
        else:
            print("Error with Addition of "+str(name)+" from course " + str(course) +".")