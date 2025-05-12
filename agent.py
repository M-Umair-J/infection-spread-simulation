import random

class Agent:
    base_infection_probability = 0.3
    def __init__(self,id,age,immunity,mobility,cluster=None):
        self.id = id
        self.age = age
        self.status = "S"
        self.infected_already = False
        self.immunity = immunity
        self.mobility = mobility
        self.last_infected_timestep = -1
        self.cluster = cluster
        self.neighbours = []
        
    def decide_to_infect_neighbours(self):
        count_to_infect = int(len(self.neighbours) * self.mobility)
        return random.sample(self.neighbours,min(count_to_infect,len(self.neighbours)))
    
    def attempt_to_infect_neighbour(self, neighbour_agent, timestep):
        if self.status == "I" and neighbour_agent.status == "S":
            prob = (self.base_infection_probability * self.immunity)
            if self.age>20 and self.age<40:
                prob = 0.2 * prob
            else:
                prob = 0.4 * prob        

            if random.random() < prob:
                neighbour_agent.infect(timestep)

    def infect(self,timestep):
        self.status = "I"
        self.last_infected_timestep = timestep

    def recover(self,timestep,recovery_time):
        if self.status == "I" and (timestep-self.last_infected_timestep)>=recovery_time and self.immunity > 0.9:
            self.status = "R"
    
    def start(self,agents,timestep,recovery_time):
        if self.status == "I":
            for neighbour_id in self.decide_to_infect_neighbours():
                self.attempt_to_infect_neighbour(agents[neighbour_id],timestep)
            self.recover(timestep,recovery_time)