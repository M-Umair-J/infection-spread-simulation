import matplotlib.pyplot as pt
import networkx
import random
import agent


num_agents = 100
recovery_time = 30
initially_infected = 8
Graph = networkx.watts_strogatz_graph(num_agents,7,0.3)
agents = {}

for i in Graph.nodes():
    mobility = random.uniform(0.3,1)
    immunity = 0.1
    age = random.randint(0,100)
    agents[i] = agent.Agent(i,age,immunity,mobility)


for u, v in Graph.edges():
    agents[u].neighbours.append(v)
    agents[v].neighbours.append(u)


for i in random.sample(list(agents.keys()),initially_infected):
    agents[i].infect(0)


pos = networkx.spring_layout(Graph)


days = 100
history = [] 
def start_simulation():
    pt.ion()  
    fig, ax = pt.subplots(figsize=(8, 6))

    for timestep in range(days):
        ax.clear()

        i = 0
        for agent in agents.values():
            agent.immunity = agent.immunity + random.uniform(0.02,0.2)
            recovery_time = int(agent.immunity * random.randint(5,15))
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
