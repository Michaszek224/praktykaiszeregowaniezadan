import sys
import time
import random

def convert_to_batches(genome):
    number_of_batches = max(genome) + 1
    batches = []
    for i in range(number_of_batches):
        batches.append([j for j, k in enumerate(genome) if i == k])
    return batches

def load_instance():
    input_path = sys.argv[1]
    input = open(input_path, 'r').read().strip().split('\n')
    tasks = []
    n, setup_time = map(int, input[0].split())
    for i in range(1, len(input)):
        p, d = map(int, input[i].split())
        tasks.append((p, d))
    return n, setup_time, tasks, float(sys.argv[3])

def save_result(tardiness, genome):
    output_path = sys.argv[2]
    with open(output_path, 'w') as f:
        f.write(f'{tardiness}\n')
        batches = convert_to_batches(genome)
        f.write(f'{len(batches)}\n')
        for batch in batches:
            f.write(' '.join([str(i + 1) for i in batch]) + '\n')

def create_population(n, tasks, size):
    number_of_batches = random.randint(2, n // 2)
    population = []
    task_order = sorted(range(n), key=lambda x: (tasks[x][1], -tasks[x][0]))
    for _ in range(size):
        genome = [-1] * n
        batch_sizes = [1] * number_of_batches

        remaining_tasks = n - number_of_batches
        for _ in range(remaining_tasks):
            batch_sizes[random.randint(0, number_of_batches - 1)] += 1

        task_order_index = 0
        for batch_index in range(number_of_batches):
            for _ in range(batch_sizes[batch_index]):
                genome[task_order[task_order_index]] = batch_index
                task_order_index += 1

        population.append(genome)
    return population

def fitness(setup_time, tasks, genome):
    current_time = 0
    tardiness = 0
    batches = convert_to_batches(genome)
    for batch in batches:
        if current_time > 0:
            current_time += setup_time
        current_time += sum(tasks[i][0] for i in batch)
        tardiness += sum(max(0, current_time - tasks[i][1]) for i in batch)
    return tardiness

def crossover(parent1, parent2):
    number_of_batches = max(parent1) + 1
    cut = random.randint(1, len(parent1) - 1)
    children = [parent1[:cut] + parent2[cut:], parent2[:cut] + parent1[cut:]]

    for child in children:
        empty_batches = set(range(max(child) + 1)) - set(child)
        for empty_batch in empty_batches:
            donor_batch = next(batch for batch in range(number_of_batches) if child.count(batch) > 1)
            task_index = child.index(donor_batch)
            child[task_index] = empty_batch

    return children

def mutate(genome):
    task1, task2 = random.sample(range(len(genome)), 2)
    genome[task1], genome[task2] = genome[task2], genome[task1]

def main():
    start_time = time.perf_counter()
    n, setup_time, tasks, max_seconds = load_instance()

    TIME_FACTOR = 0.96
    SELECTION_FACTOR = 2
    INITIAL_POPULATION_SIZE = SELECTION_FACTOR ** 8
    MUTATION_PROBABILITY = 0.1

    min_tardiness = float('inf')
    min_genome = None
    population = create_population(n, tasks, INITIAL_POPULATION_SIZE)

    while time.perf_counter() - start_time < max_seconds * TIME_FACTOR:
        genome_with_tardiness = [(genome, fitness(setup_time, tasks, genome)) for genome in population]
        genome_with_tardiness.sort(key=lambda x: x[1])

        if genome_with_tardiness[0][1] < min_tardiness:
            min_tardiness = genome_with_tardiness[0][1]
            min_genome = genome_with_tardiness[0][0]

        if len(population) <= SELECTION_FACTOR:
            population = create_population(n, tasks, INITIAL_POPULATION_SIZE)
            continue

        selection_size = len(population) // SELECTION_FACTOR
        population = [genome_with_tardiness[i][0] for i in range(selection_size)]

        children = []
        for i in range(0, len(population), 2):
            children.extend(crossover(population[i], population[i + 1]))

        for child in children:
            if random.random() < MUTATION_PROBABILITY:
                mutate(child)

        population = children

    save_result(min_tardiness, min_genome)

if __name__ == '__main__':
    assert len(sys.argv) == 4
    main()
