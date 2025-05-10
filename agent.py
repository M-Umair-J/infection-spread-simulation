import random
import networkx
import matplotlib.pyplot as pt

class Agent:
    base_infection_probability = 0.03
    def __init__(self,id,age,immunity,mobility):
        self.id = id
        self.age = age
        self.status = "S"
        self.infected_already = False
        self.immunity = immunity
        self.mobility = mobility
        self.last_infected_timestep = -1
        self.neighbours = []
        
    def decide_to_infect_neighbours(self):
        count_to_infect = int(len(self.neighbours) * self.mobility)
        return random.sample(self.neighbours,min(count_to_infect,len(self.neighbours)))
    
    def attempt_to_infect_neighbour(self, neighbour_agent, timestep):
        if self.status == "I" and neighbour_agent.status == "S":
            prob = (self.base_infection_probability * self.mobility) / self.immunity
            if random.random() < prob:
                neighbour_agent.infect(timestep)
    def infect(self,timestep):
        self.status = "I"
        self.last_infected_timestep = timestep

    def recover(self,timestep,recovery_time):
        if self.status == "I" and (timestep-self.last_infected_timestep)>=recovery_time:
            self.status = "R"
    
    def start(self,agents,timestep,recovery_time):
        if self.status == "I":
            for neighbour_id in self.decide_to_infect_neighbours():
                self.attempt_to_infect_neighbour(agents[neighbour_id],timestep)
            self.recover(timestep,recovery_time)

num_agents = 100
recovery_time = 10
initially_infected = 10
Graph = networkx.watts_strogatz_graph(num_agents,7,0.2)
agents = {}

for i in Graph.nodes():
    mobility = random.uniform(0.3,1)
    immunity = random.uniform(0.3,1)
    age = random.randint(0,100)
    agents[i] = Agent(i,age,immunity,mobility)


for u, v in Graph.edges():
    agents[u].neighbours.append(v)
    agents[v].neighbours.append(u)


for i in random.sample(list(agents.keys()),initially_infected):
    agents[i].infect(0)


pos = networkx.spring_layout(Graph)


days = 100
history = [] 

pt.ion()  
fig, ax = pt.subplots(figsize=(8, 6))

for timestep in range(days):
    ax.clear()


    for agent in agents.values():
        agent.start(agents, timestep, recovery_time)

 
    counts = {'S': 0, 'I': 0, 'R': 0}
    for a in agents.values():
        counts[a.status] += 1
    history.append(counts)

    
    color_map = []
    for node in Graph.nodes():
        status = agents[node].status
        color_map.append({'S': 'green', 'I': 'red', 'R': 'black'}[status])

    networkx.draw(Graph, pos, node_color=color_map, node_size=40, with_labels=False, ax=ax)
    ax.set_title(f"Day {timestep} - S: {counts['S']}  I: {counts['I']}  R: {counts['R']}")
    pt.pause(0.3)

pt.ioff()
pt.show()


s_vals = [day['S'] for day in history]
i_vals = [day['I'] for day in history]
r_vals = [day['R'] for day in history]

pt.figure(figsize=(10, 5))
pt.plot(s_vals, label='Susceptible', color='green')
pt.plot(i_vals, label='Infected', color='red')
pt.plot(r_vals, label='Recovered', color='gray')
pt.xlabel("Timestep (Day)")
pt.ylabel("Number of Agents")
pt.title("SIR Agent-Based Simulation")
pt.legend()
pt.grid(True)
pt.tight_layout()
pt.show()
