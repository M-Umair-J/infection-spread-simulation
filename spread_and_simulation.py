import matplotlib.pyplot as pt
import networkx
import random
import agent


num_agents = 100
recovery_time = 30
initially_infected = 8
Graph = networkx.watts_strogatz_graph(num_agents,10,0.03)
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



pos = networkx.spring_layout(Graph, k=0.3, iterations=100, seed=42)



days = 100
history = [] 
def start_simulation():
    pt.ion()  
    fig, ax = pt.subplots(figsize=(16, 12))
    ax.set_aspect('equal')
    ax.set_facecolor('#e6f7ff')
    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-1.5, 1.5)
    

    for timestep in range(days):
        ax.clear()
        ax.set_facecolor('#e6f7ff')
        ax.set_xlim(-1.5, 1.5)
        ax.set_ylim(-1.5, 1.5)

        i = 0
        for agent in agents.values():
            agent.immunity = agent.immunity + random.uniform(0.02,0.2)
            recovery_time = int(agent.immunity * random.randint(5,15))
            agent.start(agents, timestep, recovery_time)

 
        counts = {'S': 0, 'I': 0, 'R': 0}
        for a in agents.values():
            counts[a.status] += 1
        history.append(counts)

        
        node_sizes = []
        for node in Graph.nodes():
            base_size = 60
            degree = Graph.degree(node)
            node_sizes.append(base_size + degree * 2)
        
        color_map = []
        for node in Graph.nodes():
            status = agents[node].status
            colors = {'S': '#00cc66', 'I': '#ff3333', 'R': '#404040'} 
            color_map.append(colors[status])
        
        
        networkx.draw_networkx_edges(Graph, pos, alpha=0.1, width=0.5, edge_color='#333333')
        
        
        networkx.draw_networkx_nodes(
            Graph, 
            pos, 
            node_color=color_map, 
            node_size=node_sizes, 
            alpha=0.9,
            edgecolors='white',
            linewidths=0.5
        )
        
        susceptible_patch = pt.Line2D([0], [0], marker='o', color='w', 
                                    markerfacecolor='#00cc66', markersize=10, label=f'Susceptible: {counts["S"]}')
        infected_patch = pt.Line2D([0], [0], marker='o', color='w', 
                                    markerfacecolor='#ff3333', markersize=10, label=f'Infected: {counts["I"]}')
        recovered_patch = pt.Line2D([0], [0], marker='o', color='w', 
                                    markerfacecolor='#404040', markersize=10, label=f'Recovered: {counts["R"]}')
        ax.legend(handles=[susceptible_patch, infected_patch, recovered_patch], 
                loc='upper right', frameon=True, facecolor='white')
        
        ax.set_title(f"Day {timestep} - Disease Spread Simulation", fontsize=14, fontweight='bold')
        pt.tight_layout()
        pt.pause(0.3)

    pt.ioff()
    pt.show()

    s_vals = [day['S'] for day in history]
    i_vals = [day['I'] for day in history]
    r_vals = [day['R'] for day in history]

    pt.figure(figsize=(12, 6))
    pt.plot(s_vals, label='Susceptible', color='#00cc66', linewidth=3)
    pt.plot(i_vals, label='Infected', color='#ff3333', linewidth=3)
    pt.plot(r_vals, label='Recovered', color='#404040', linewidth=3)
    pt.xlabel("Timestep (Day)", fontsize=12)
    pt.ylabel("Number of Agents", fontsize=12)
    pt.title("SIR Agent-Based Simulation Results", fontsize=14, fontweight='bold')
    pt.legend(fontsize=12)
    pt.grid(True, alpha=0.3)
    pt.tight_layout()
    pt.show()