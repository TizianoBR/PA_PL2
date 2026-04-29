#!/usr/bin/env python3

########################################################################################
# Problem instance generator skeleton for emergencies drones domain.
# Based on the Linköping University TDDD48 2021 course.
# https://www.ida.liu.se/~TDDD48/labs/2021/lab1/index.en.shtml
#
# You mainly have to change the parts marked as TODO.
#
########################################################################################


from optparse import OptionParser
import random
import math
import sys

########################################################################################
# Hard-coded options
########################################################################################

# Crates will have different contents, such as food and medicine.
# You can change this to generate other contents if you want.

content_types = ["food", "medicine"]


########################################################################################
# Random seed
########################################################################################

# Set seed to 0 if you want more predictability...
# random.seed(0);

########################################################################################
# Helper functions
########################################################################################

# We associate each location with x/y coordinates.  These coordinates
# won't actually be used explicitly in the domain, but we *will*
# eventually use them implicitly by using *distances* in order to
# calculate flight times.
#
# This function returns the euclidean distance between two locations.
# The locations are given via their integer index.  You won't have to
# use this other than indirectly through the flight cost function.
def distance(location_coords, location_num1, location_num2):
    x1 = location_coords[location_num1][0]
    y1 = location_coords[location_num1][1]
    x2 = location_coords[location_num2][0]
    y2 = location_coords[location_num2][1]
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


# This function returns the action cost of flying between two
# locations supplied by their integer indexes.  You can use this
# function when you extend the problem generator to generate action
# costs.
def flight_cost(location_coords, location_num1, location_num2):
    return int(distance(location_coords, location_num1, location_num2)) + 1


# When you run this script you specify the *total* number of crates
# you want.  The function below determines randomly which crates
# will have a specific type of contents.  crates_with_contents[0]
# is a list of crates containing content_types[0] (in our
# example "food"), and so on.
# Note: Will have at least one crate per type!

def setup_content_types(options):
    while True:
        num_crates_with_contents = []
        crates_left = options.crates
        for x in range(len(content_types) - 1):
            types_after_this = len(content_types) - x - 1
            max_now = crates_left - types_after_this
            # print x, types_after_this, crates_left, len(content_types), max_now
            num = random.randint(1, max_now)
            # print num
            num_crates_with_contents.append(num)
            crates_left -= num
        num_crates_with_contents.append(crates_left)
        # print(num_crates_with_contents)

        # If we have 10 medicine and 4 food, with 7 people,
        # we can support at most 7+4=11 goals.
        maxgoals = sum(min(num_crates, options.persons) for num_crates in num_crates_with_contents)

        # Check if the randomization supports the number of goals we want to generate.
        # Otherwise, try to randomize again.
        if options.goals <= maxgoals:
            # Done
            break

    print()
    print("Types\tQuantities")
    for x in range(len(num_crates_with_contents)):
        if num_crates_with_contents[x] > 0:
            print(content_types[x] + "\t " + str(num_crates_with_contents[x]))

    crates_with_contents = []
    counter = 1
    for x in range(len(content_types)):
        crates = []
        for y in range(num_crates_with_contents[x]):
            crates.append("crate" + str(counter))
            counter += 1
        crates_with_contents.append(crates)

    return crates_with_contents


# This function populates the location_coords list with an X and Y
# coordinate for each location.  You won't have to use this other than
# indirectly through the flight cost function.
def setup_location_coords(options):
    location_coords = [(0, 0)]  # For the depot
    for x in range(1, options.locations + 1):
        location_coords.append((random.randint(1, 200), random.randint(1, 200)))

    print("Location positions", location_coords)
    return location_coords


# This function generates a random set of goals.
# After you run this, need[personid][contentid] is true if and only if
# the goal is for the person to have a crate with the specified content.
# You will use this to create goal statements in PDDL.
def setup_person_needs(options, crates_with_contents):
    need = [[False for i in range(len(content_types))] for j in range(options.persons)]
    goals_per_contents = [0 for i in range(len(content_types))]

    for goalnum in range(options.goals):

        generated = False
        while not generated:
            rand_person = random.randint(0, options.persons - 1)
            rand_content = random.randint(0, len(content_types) - 1)
            # If we have enough crates with that content
            # and the person doesn't already need that content
            if (goals_per_contents[rand_content] < len(crates_with_contents[rand_content])
                    and not need[rand_person][rand_content]):
                need[rand_person][rand_content] = True
                goals_per_contents[rand_content] += 1
                generated = True
    return need


########################################################################################
# Main program
########################################################################################

def main():
    parser = OptionParser(usage='python generator_shop.py [-help] options...')
    parser.add_option('-d', '--drones', dest='drones', type=int, help='number of drones')
    parser.add_option('-r', '--transporters', type=int, dest='transporters', help='number of transporters')
    parser.add_option('-l', '--locations', type=int, dest='locations', help='number of locations (excl. depot)')
    parser.add_option('-p', '--persons', type=int, dest='persons', help='number of persons')
    parser.add_option('-c', '--crates', type=int, dest='crates', help='number of crates')
    parser.add_option('-g', '--goals', type=int, dest='goals', help='number of goals')
    parser.add_option('-o', '--output', dest='output', default='problem', help='output problem file name')

    (options, args) = parser.parse_args()

    # Validaciones básicas
    if any(opt is None for opt in [options.drones, options.locations, options.persons, options.crates, options.goals]):
        print("Error: Faltan argumentos. Use --help.")
        sys.exit(1)

    # Listas de objetos
    drone = ["drone" + str(x + 1) for x in range(options.drones)]
    location = ["depot"] + ["loc" + str(x + 1) for x in range(options.locations)]
    person = ["person" + str(x + 1) for x in range(options.persons)]
    
    crates_with_contents = setup_content_types(options)
    need = setup_person_needs(options, crates_with_contents)

    problem_name = options.output

    with open(problem_name, 'w') as f:
        # Estructura SHOP2: (defproblem nombre_problema nombre_dominio (estado_inicial) (tareas))
        f.write(f"(defproblem {problem_name} emergency-logistics\n")
        
        # --- ESTADO INICIAL ---
        f.write("  (\n")
        
        # Drones en el depósito y brazos libres
        for d in drone:
            f.write(f"    (at-drone {d} depot)\n")
            f.write(f"    (arm-free-left {d})\n")
            f.write(f"    (arm-free-right {d})\n")

        # Personas en localizaciones aleatorias (no depot)
        locs_no_depot = [l for l in location if l != "depot"]
        for p in person:
            f.write(f"    (at-person {p} {random.choice(locs_no_depot)})\n")

        # Crates y sus contenidos (Ejercicio 1.1: objetos individuales)
        for i, content_name in enumerate(content_types):
            for crate_name in crates_with_contents[i]:
                f.write(f"    (at-crate {crate_name} depot)\n")
                f.write(f"    (crate-content {crate_name} {content_name})\n")

        # Necesidades (Las metas en SHOP2 son parte del estado inicial)
        for p_idx in range(options.persons):
            for c_idx in range(len(content_types)):
                if need[p_idx][c_idx]:
                    f.write(f"    (necesita {person[p_idx]} {content_types[c_idx]})\n")

        f.write("  )\n")

        # --- LISTA DE TAREAS ---
        # La tarea principal definida en tu dominio es (enviar-todo)
        f.write("  ((enviar-todo))\n")
        f.write(")\n")

    print(f"Archivo generado con éxito: {problem_name}")

if __name__ == '__main__':
    main()