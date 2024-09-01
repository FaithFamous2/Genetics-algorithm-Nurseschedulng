import random
import logging


class GeneticAlgorithm:
    def __init__(self, nurses, days, shifts, min_head_nurses_per_shift, population_size, max_generations, crossover_rate, mutation_rate):
        self.nurses = nurses
        self.days = days
        self.shifts = shifts
        self.min_head_nurses_per_shift = min_head_nurses_per_shift
        self.population_size = population_size
        self.max_generations = max_generations
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.population = []

    def initialize_population(self):
        """Initialize the population with random schedules."""
        for _ in range(self.population_size):
            schedule = self.generate_random_schedule()
            self.population.append(schedule)

    def generate_random_schedule(self):
        """Generate a random nurse schedule for all days and shifts."""
        schedule = {}
        for day in self.days:
            schedule[day] = {}
            for shift in self.shifts:
                head_nurses = random.sample(self.nurses["Head Nurse"], k=self.min_head_nurses_per_shift)
                junior_nurses = random.sample(self.nurses["Junior Nurse"], k=random.randint(1, len(self.nurses["Junior Nurse"])))
                schedule[day][shift] = {"Head Nurse": head_nurses, "Junior Nurse": junior_nurses}
        return schedule

    def fitness(self, schedule):
        """Evaluate the fitness score of a schedule."""
        score = 0
        for day in schedule:
            for shift in schedule[day]:
                # Constraint 1: Minimum number of head nurses per shift
                if len(schedule[day][shift]["Head Nurse"]) >= self.min_head_nurses_per_shift:
                    score += 1

                # Constraint 2: Ensure unique nurses in every shift per day
                all_nurses = schedule[day][shift]["Head Nurse"] + schedule[day][shift]["Junior Nurse"]
                if len(all_nurses) == len(set(all_nurses)):
                    score += 1
        return score

    def selection(self):
        """Select individuals for crossover using tournament selection."""
        tournament_size = 3
        tournament = random.sample(self.population, tournament_size)
        fittest = max(tournament, key=lambda s: self.fitness(s))
        return fittest

    def crossover(self, parent1, parent2):
        """Perform crossover between two parent schedules."""
        child = {}
        for day in self.days:
            child[day] = {}
            for shift in self.shifts:
                if random.random() < self.crossover_rate:
                    child[day][shift] = parent1[day][shift]
                else:
                    child[day][shift] = parent2[day][shift]
        return child

    def mutate(self, schedule):
        """Mutate a schedule to introduce variations."""
        for day in self.days:
            for shift in self.shifts:
                if random.random() < self.mutation_rate:
                    # Randomly change the junior nurses in a shift
                    schedule[day][shift]["Junior Nurse"] = random.sample(self.nurses["Junior Nurse"], k=random.randint(1, len(self.nurses["Junior Nurse"])))
        return schedule

    def evolve(self):
        """Evolve the population over generations."""
        new_population = []
        for _ in range(self.population_size):
            parent1 = self.selection()
            parent2 = self.selection()
            child = self.crossover(parent1, parent2)
            child = self.mutate(child)
            new_population.append(child)
        self.population = new_population

    def run(self):
        """Run the Genetic Algorithm to find the best nurse schedule."""
        self.initialize_population()
        for generation in range(self.max_generations):
            self.evolve()
        best_schedule = max(self.population, key=lambda s: self.fitness(s))
        return best_schedule
