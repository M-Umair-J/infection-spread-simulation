import random

class Agent:
    base_infection_probability = 0.3
    def __init__(self, id, age, immunity, mobility, cluster=None):
        self.id = id
        self.age = age
        self.immunity = immunity
        self.mobility = mobility
        self.cluster = cluster
        self.status = "S"  # S: susceptible, I: infected, R: recovered, D: dead
        self.neighbours = set()
        self.last_infected_timestep = -1
        self.recovery_time = random.randint(10, 16)  # Random recovery time between 10-16 days

    def decide_to_infect_neighbours(self):
        count_to_infect = int(len(self.neighbours) * self.mobility)
        if len(self.neighbours) == 0 or count_to_infect <= 0:
            return []
        neighbors_list = sorted(self.neighbours)#convert set to list for sampling
        sample_size = min(count_to_infect, len(neighbors_list))#calculate actual number for sampling
        return random.sample(neighbors_list, sample_size)
    
    def attempt_to_infect_neighbour(self, neighbour_agent, timestep):
        if self.status == "I" and neighbour_agent.status == "S":
            # Base probability
            base_prob = 0.15  # Lower base probability
            
            # Age-based risk factors for infection transmission
            if self.age < 18:
                transmitter_factor = 0.8  # Children may transmit less
            elif 18 <= self.age < 60:
                transmitter_factor = 1.0  # Adults normal transmission
            else:
                transmitter_factor = 0.9  # Elderly may have fewer contacts but higher viral load
                
            # Age-based susceptibility of receiver
            if neighbour_agent.age < 18:
                receiver_factor = 0.7  # Children may be less susceptible
            elif 18 <= neighbour_agent.age < 60:
                receiver_factor = 1.0  # Adults normal susceptibility
            else:
                receiver_factor = 1.5  # Elderly more susceptible
                
            # Immunity factor (stronger effect)
            immunity_factor = 1 - (neighbour_agent.immunity * neighbour_agent.immunity)  # Square makes immunity more significant
            
            # Calculate final probability
            prob = base_prob * transmitter_factor * receiver_factor * immunity_factor
            
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
    
    def update_status(self, agents, timestep):
        if self.status == "I" and (timestep - self.last_infected_timestep) >= self.recovery_time:
            # Agent has reached their recovery time
            return True
        return False