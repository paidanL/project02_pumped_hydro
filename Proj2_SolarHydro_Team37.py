# Project 2: An optimization model for a Pumped Hydro Electric Storage facility
# File: Proj2_SolarHydro_Team37.py
# Date: 17 October 2020
# By: Moses Hamm, P. Aidan Leib, Aakar Jain, Gage Detchemendy
# hammmj
# pleib
# jain377
# gdetchem
# Section: 3
# Team: 37
#
# ELECTRONIC SIGNATURE
# Moses Hamm, P. Aidan Leib, Aakar Jain, Gage Detchemendy
#
# The electronic signature above indicates that the program
# submitted for evaluation is team 37's work. We have
# a general understanding of all aspects of its development
# and execution.
#
# DESCRIPTION: This program provides a comprehensive model for a Pumped Hydro
# Electric Storage facility using various real world parameters.


#---------------------------------------------------
#  Imports
#---------------------------------------------------
import numpy as np
import math


#---------------------------------------------------
#  Functions
#---------------------------------------------------
def sortByCost(x):
    optimum = x[-1]
    return(optimum)


def sortByEfficiency(x):
    optimum = x[-2] / x[0]
    return(optimum)


def sortByBoth(x):
    optimum = (x[-2] / x[0]) / x[-1]
    return(optimum)


#---------------------------------------------------
#  Input
#---------------------------------------------------
print("What would you like to sort results by?")
userSort = input("Please enter 'Cost', 'Efficiency', or 'Both': ")


#---------------------------------------------------
#  Variables
#---------------------------------------------------
upResults = []
outResults = []

message = ''

pumpEfficiency = np.linspace(0.8, 0.92, num=5)
turbineEfficiency = [0.94, 0.92, 0.89, 0.86, 0.83]
diameterUp = [1.5, 1.75, 2., 2.25, 2.5, 2.75, 3.]
darcyUp = [0.002, 0.005, 0.01, 0.02, 0.03, 0.05]
pumpQ = np.linspace(500, 1, num=25)
turbineQ = np.linspace(1, 500, num=25)
resWallUp = np.linspace(5, 20, num=7)
resRadiusUp = np.linspace(1, 300, num=30)


try:
    with open('./Final_Results.txt', 'r') as fid:
        print('\nReading file...')
        outResults = [x.rstrip('\n').split() for x in fid.readlines()]

        for row in outResults:
            for x in range(0, len(row)):
                row[x] = float(row[x])

except FileNotFoundError:
    print("\nStarting calculations!")
    print('Please wait ~20 minutes...')

    #---------------------------------------------------
    #  First set of Calculations
    #---------------------------------------------------
    # for calculating eIn first

    for n in pumpEfficiency:
        for d in diameterUp:
            for darcy in darcyUp:
                for q in pumpQ:
                    for height in resWallUp:
                        for radius in resRadiusUp:

                            eIn = (((math.pi * (radius ** 2) * height * 1000 * 9.8 * (30 + (height / 2))) +
                                    (math.pi * (radius ** 2) * height * 1000 * darcy * math.sqrt(4500) * ((q / (math.pi * ((d / 2) ** 2))) ** 2) / (2 * d)) +
                                    (math.pi * (radius ** 2) * height * 1000 * 0.15 * ((q / (math.pi * ((d / 2) ** 2))) ** 2))) / n)

                            # conversion factor from Joules to MWh
                            eIn = eIn / (3.6 * 10**9)

                            # sorts only the feasible combinations
                            if eIn >= 120:
                                newList = [eIn, round(n, 2), round(
                                    d, 2), round(darcy, 4), q, height, radius]
                                upResults.append(newList)

    upResults.sort()
    print("\nFinished calculating all 'Energy In' values!")  # checkpoint print

    # opens a file containing the pipe shack values from the table given in parts catalog
    fid = open('./pipes_shack.txt', 'r')

    # adds all the lines from the file to a 2D array, simulating a table
    pipes_shack = [x.rstrip('\n').split() for x in fid.readlines()]

    fid.close()

    # takes every value in the table and changes it to a float
    for row in pipes_shack:
        for x in range(0, len(row)):
            row[x] = float(row[x])

    #---------------------------------------------------
    #  Second set of Calculations
    #---------------------------------------------------

    for i in upResults:
        for z in turbineQ:
            for m in turbineEfficiency:
                oldResults = i.copy()

                l = math.sqrt(4500)  # length of pipe at zone 1
                eIn = i[0] * (3.6 * 10**9)  # Ein (Joules)
                n = i[1]  # eta p
                d = i[2]  # pipe diameter
                darcy = i[3]  # f
                q = i[4]  # q up
                height = i[5]  # 1/2 height of reservoir wall
                radius = i[6]  # radius of reservoir
                a = math.pi * ((d / 2)**2)  # cross sectional area of pipe
                A = math.pi * radius**2  # Area of reservoir

                eOut = (eIn * n * m) - ((A * height * 1000 * m) / a**2) * \
                       (((darcy * l) / (2 * d)) + 0.15) * (q**2 + z**2)

                # conversion factor again
                eOut = eOut / (3.6 * 10**9)

                fillTime = math.pi * (radius ** 2) * height / (q)
                drainTime = math.pi * (radius ** 2) * height / z

                # another filter
                if eOut >= 120 and fillTime <= 43200 and drainTime <= 43200:
                    oldResults.append(round(m, 2))
                    oldResults.append(z)
                    oldResults.append(fillTime)
                    oldResults.append(drainTime)
                    oldResults.append(eOut)

                    outResults.append(oldResults.copy())

                    oldResults.clear()

    print("\nFinished calculating all 'Energy Out' values!")  # checkpoint print

    #---------------------------------------------------
    #  Cost Calculations
    #---------------------------------------------------

    # for-loop calculates the overall cost for each iteration and adds that value to the
    # end of the list with the rest of the iteration's values

    for element in outResults:
        n = element[1]
        d = element[2]
        darcy = element[3]
        q = element[4]
        height = element[5]
        radius = element[6]
        turbineEfficiency = element[7]
        turbineQ = element[8]

        area = math.pi * radius**2  # area of reservoir
        perimeter = 2 * math.pi * radius  # perimeter of reservoir

        # cost of each meter length of pipe
        darcy_cost = float(
            pipes_shack[diameterUp.index(d)][darcyUp.index(darcy)])

        # reservoir costs
        if (height == 5):
            wall_cost = 30 * perimeter
        elif (height == 7.5):
            wall_cost = 60 * perimeter
        elif (height == 10):
            wall_cost = 95 * perimeter
        elif (height == 12.5):
            wall_cost = 135 * perimeter
        elif (height == 15):
            wall_cost = 180 * perimeter
        elif (height == 17.5):
            wall_cost = 250 * perimeter
        elif (height == 20):
            wall_cost = 340 * perimeter

        # pump cost calculation
        if (n == 0.8):
            pumpEfficiency_cost = 220 * q
        elif (n == 0.83):
            pumpEfficiency_cost = 264 * q
        elif (n == 0.86):
            pumpEfficiency_cost = 317 * q
        elif (n == 0.89):
            pumpEfficiency_cost = 380 * q
        elif (n == 0.92):
            pumpEfficiency_cost = 456 * q

        # bend cost calculations
        if (d == 0.1):
            bend_cost = 2.1
        elif (d == 0.25):
            bend_cost = 3.14
        elif (d == 0.5):
            bend_cost = 10.34
        elif (d == 0.75):
            bend_cost = 30
        elif (d == 1):
            bend_cost = 68
        elif (d == 1.25):
            bend_cost = 130
        elif (d == 1.5):
            bend_cost = 224
        elif (d == 1.75):
            bend_cost = 356
        elif (d == 2):
            bend_cost = 530
        elif (d == 2.25):
            bend_cost = 754
        elif (d == 2.5):
            bend_cost = 1032
        elif (d == 2.75):
            bend_cost = 1374
        elif (d == 3):
            bend_cost = 1784

        # turbine cost calculations
        if (turbineEfficiency == 0.83):
            turbineEfficiency_cost = 396 * turbineQ
        elif (turbineEfficiency == 0.86):
            turbineEfficiency_cost = 475 * turbineQ
        elif (turbineEfficiency == 0.89):
            turbineEfficiency_cost = 570 * turbineQ
        elif (turbineEfficiency == 0.92):
            turbineEfficiency_cost = 684 * turbineQ
        elif (turbineEfficiency == 0.94):
            turbineEfficiency_cost = 821 * turbineQ

        # overall cost equation:
        cost = ((wall_cost + (.25 * area) + pumpEfficiency_cost + (math.sqrt(4500) * 500) +
                 (darcy_cost * math.sqrt(4500)) + bend_cost) + turbineEfficiency_cost)

        element.append(cost)

    print("\nAll costs calculated!")  # Another checkpoint

    # writes all feasible combinations to a file for faster reference

    with open('./Final_Results.txt', 'w') as fid:
        print("\nWriting combinations to the file 'Final_Results.txt'...")
        for element in outResults:
            for x in element:
                fid.writelines(format(x, '^13,.4') + ' ')

            fid.writelines('\n')


# sorts the final array by the weighted values for energy effciency and cost

if (userSort.title() == 'Cost'):
    outResults.sort(key=sortByCost, reverse=False)
    message = 'Lowest Cost Outcome'

elif (userSort.title() == 'Efficiency'):
    outResults.sort(key=sortByEfficiency, reverse=True)
    message = 'Most Efficient Outcome'

else:
    outResults.sort(key=sortByBoth, reverse=True)
    message = 'Most Efficient for Least Cost'


#---------------------------------------------------
#  Summary of Optimal Facility
#---------------------------------------------------
print(f"\n----- {message} -----\n")

print("Energy In: " + format(outResults[0][0], ',.4f') + " MWh")
print("Energy Out: " + format(outResults[0][-2], ',.4f') + " MWh")
print("Energy Effciency: " +
      format((outResults[0][-2] / outResults[0][0]), '.2%'))
print("Cost: $" + format(outResults[0][-1] + 150000, ',.2f'))
print("Cost Per MegaWatt Hour Out: $" +
      format(((outResults[0][-1] + 150000) / outResults[0][-2]), ',.2f'))
print(f"Pump Efficiency: {outResults[0][1]}")
print("Pump Volumetric Flow Rate: " +
      format(outResults[0][8], ',.2f') + " m^3/s")
print(f"Turbine Efficiency: {outResults[0][7]}")
print("Turbine Volumetric Flow Rate: " +
      format(outResults[0][8], ',.2f') + " m^3/s")
print(f"Pipe Diameter: {outResults[0][2]} m")
print(f"Darcy Friction Factor: {outResults[0][3]}")
print("Reservoir Radius: " + format(outResults[0][6], ',.2f') + " m")
print(f"Reservoir Wall Height: {outResults[0][5]} m")
