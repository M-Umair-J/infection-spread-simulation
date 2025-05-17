import random

class Agent:
    base_infection_probability = 0.3
    def __init__(self,id,age,immunity,mobility,cluster=None):
        self.id = id
        self.age = age
        self.status = "S"
        # self.infected_already = False
        self.immunity = immunity
        self.mobility = mobility
        self.last_infected_timestep = -1
        self.cluster = cluster
        self.neighbours = set()
        
    # def decide_to_infect_neighbours(self):
    #     count_to_infect = int(len(self.neighbours) * self.mobility)
    #     return random.sample(self.neighbours,min(count_to_infect,len(self.neighbours)))

    def decide_to_infect_neighbours(self):
        count_to_infect = int(len(self.neighbours) * self.mobility)
        #convert set to list for sampling
        if len(self.neighbours) == 0 or count_to_infect <= 0:
            return []
        #convert to sorted list
        neighbors_list = sorted(self.neighbours)
        #calculate actual number to sample 
        sample_size = min(count_to_infect, len(neighbors_list))
        return random.sample(neighbors_list, sample_size)
    
    def attempt_to_infect_neighbour(self, neighbour_agent, timestep):
        if self.status == "I" and neighbour_agent.status == "S":
            age_factor = 0.2 if 20 < self.age < 40 else 0.4
            prob = self.base_infection_probability * age_factor * (1 - neighbour_agent.immunity)
            
            if random.random() < prob:
                neighbour_agent.infect(timestep)
                return True
        return False

    def infect(self,timestep):
        if self.status == "S":
            self.status = "I"
            self.last_infected_timestep = timestep

    def recover(self,timestep,recovery_time,statuses_list):
        if self.status == "I" and (timestep-self.last_infected_timestep)>=recovery_time and self.immunity > 0.9:
            self.status = "R"
            statuses_list["I"] -= 1 
            statuses_list["R"] += 1
    
    def update_status(self,agents, timestep, recovery_time, mortality_rate):
        if self.status == "I" and (timestep - self.last_infected_timestep) >= recovery_time:
            if random.random() < mortality_rate:
                self.status = "D"
                for nodes in self.neighbours.copy():#remove from network
                    agents[nodes].neighbours.discard(self.id)
                self.neighbours.clear()
            else:
                self.status = "R"