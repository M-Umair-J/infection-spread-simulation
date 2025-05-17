import pygame
import random
import networkx as nx

def run_visualization(agents, width=1024, height=768, fps=60):
    pygame.init()
    screen = pygame.display.set_mode((width, height))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont('Arial', 16)

    #parameters for simulation
    initial_infection_rate = 0.05
    recovery_time = 14
    mortality_rate = 0.01
    time_step = 0
    simulation_paused = False
    zoom_level = 1.0
    simulation_speed = 1

    #initialize infections
    num_initial_infected = int(len(agents) * initial_infection_rate)
    initial_infected = random.sample(list(agents.keys()), num_initial_infected)
    #keeping the track of status
    status_counts = {
        "S": len(agents) - num_initial_infected,
        "I": num_initial_infected,
        "R": 0,
        "D": 0
    }

    for nodes in initial_infected:
        agents[nodes].infect(0)

    

    #create NetworkX graph (to visualize the population)
    G = nx.Graph()
    for agent_id, agent_obj in agents.items():
        G.add_node(agent_id, cluster=agent_obj.cluster)
        for neighbor in agent_obj.neighbours:
            G.add_edge(agent_id, neighbor)

    #calculating initial layout
    positions = nx.spring_layout(G, iterations=50) #spring layout for forced directed graph
    max_x = max(pos[0] for pos in positions.values()) or 1
    min_x = min(pos[0] for pos in positions.values()) or 0
    max_y = max(pos[1] for pos in positions.values()) or 1
    min_y = min(pos[1] for pos in positions.values()) or 0

    #storing base positions
    base_positions = {}
    for agent_id, pos in positions.items():
        scaled_x = (pos[0] - min_x) / (max_x - min_x) * (width - 100) + 50
        scaled_y = (pos[1] - min_y) / (max_y - min_y) * (height - 100) + 50
        base_positions[agent_id] = (scaled_x, scaled_y)
        agents[agent_id].pos = (scaled_x, scaled_y)
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    simulation_paused = not(simulation_paused)
                elif event.key == pygame.K_UP:
                    simulation_speed = min(5, simulation_speed + 0.5)
                elif event.key == pygame.K_DOWN:
                    simulation_speed = max(0.1, simulation_speed - 0.5)

            if not (simulation_paused):
                for _ in range(int(simulation_speed)):
                    new_infections = []
                    #handling infections
                    for agent in agents.values():
                        if agent.status == "I":
                            #attempt to infect
                            for neighbour_id in agent.decide_to_infect_neighbours():
                                if agents[neighbour_id].status == "S":
                                    if agent.attempt_to_infect_neighbour(agents[neighbour_id], time_step):
                                        new_infections.append(neighbour_id)
                    status_counts["S"] -= len(new_infections)
                    status_counts["I"] += len(new_infections)

                    #handling deaths and recovery
                    for agent in agents.values():
                        previous_status = agent.status
                        agent.update_status(agents, time_step, recovery_time, mortality_rate)
                        if agent.status != previous_status:
                            status_counts[previous_status] -= 1
                            status_counts[agent.status] += 1
                            if agent.status == "D": #removing dead nodes from simulation
                                if agent.id in base_positions:
                                    del base_positions[agent.id]
                    time_step += 1
         #drawing directly in main loop
        screen.fill((30, 30, 30))
        
        #drawing edges
        for agent in list(agents.values()):
            if agent.status == "D":
                del agents[agent.id]
                continue
            for nid in agent.neighbours:
                if nid > agent.id and agents[nid].status != "D":  # Avoid duplicates
                    pygame.draw.aaline(screen, (150,150,150), 
                                     (int(agent.pos[0]), int(agent.pos[1])),
                                     (int(agents[nid].pos[0]), int(agents[nid].pos[1])))

        #drawing nodes
        for agent in agents.values():
            color = (
                (40,40,40) if agent.status == "D" else
                (200,0,0) if agent.status == "I" else
                (0,0,200) if agent.status == "R" else
                (0,200,0)
            )
            pygame.draw.circle(screen, color, 
                             (int(agent.pos[0]), int(agent.pos[1])), 
                             max(1, int(5 * zoom_level)))

        #drawing UI
        y = 10
        for text in [
            f"Time: {time_step}",
            f"Speed: {simulation_speed}x",
            f"Paused: {simulation_paused}",
            f"S: {status_counts['S']}",
            f"I: {status_counts['I']}",
            f"R: {status_counts['R']}",
            f"D: {status_counts['D']}"
        ]:
            screen.blit(font.render(text, True, (255,255,255)), (10, y))
            y += 20


                    # simulation_step()
                    # draw_edges()
                    # draw_nodes()
                    # draw_ui()
        pygame.display.flip()
        clock.tick(fps)

    pygame.quit()

    # def update_network():
    #     nonlocal G
    #     G = nx.Graph()
    #     for aid, agent in agents.items():
    #         if agent.status != "D":
    #             G.add_node(aid)
    #             for nid in agent.neighbours:
    #                 if agents[nid].status != "D" and nid > aid:
    #                     G.add_edge(aid, nid)

    # def simulation_step():
    #     """Advance the simulation by one time step"""
    #     nonlocal time_step, status_counts
    
    #     # Process all agents
    #     for agent in agents.values():
    #         if agent.status == "D":
    #             continue
            
    #         # Original agent logic
    #         agent.start(agents, time_step, recovery_time)
            
    #         # Handle mortality after recovery period
    #         if (agent.status == "I" and 
    #             (time_step - agent.last_infected_timestep) >= recovery_time):
    #             if random.random() < mortality_rate:
    #                 # Remove from network
    #                 for nid in agent.neighbours.copy():
    #                     agents[nid].neighbours.discard(agent.id)
    #                 agent.neighbours.clear()
    #                 agent.status = "D"
    #                 status_counts["I"] -= 1
    #                 status_counts["D"] += 1
    #                 update_network()

    #     # Update counters
    #     current_counts = {"S":0, "I":0, "R":0, "D":0}
    #     for agent in agents.values():
    #         current_counts[agent.status] += 1
    #     status_counts.update(current_counts)
        
    #     time_step += 1

    # def draw_edges():
    #     """Draw edges using anti-aliased lines"""
    #     for u, v in G.edges():
    #         if u in agents and v in agents:
    #             start_pos = (int(agents[u].pos[0]), int(agents[u].pos[1]))
    #             end_pos = (int(agents[v].pos[0]), int(agents[v].pos[1]))
    #             pygame.draw.aaline(screen, (150,150,150), start_pos, end_pos)

    # def draw_nodes():
    #     """Draw nodes with status-appropriate colors"""
    #     for agent in agents.values():
    #         if agent.status == "D":
    #             color = (40, 40, 40)  # Dead (dark gray)
    #         elif agent.status == "I":
    #             color = (200, 0, 0)   # Infected (red)
    #         elif agent.status == "R":
    #             color = (0, 0, 200)   # Recovered (blue)
    #         else:
    #             color = (0, 200, 0)   # Susceptible (green)
            
    #         radius = max(1, int(5 * zoom_level))
    #         pos = (int(agent.pos[0]), int(agent.pos[1]))
    #         pygame.draw.circle(screen, color, pos, radius)

    # def draw_ui():
    #     """Draw simulation controls and stats"""
    #     texts = [
    #         f"Time: {time_step}",
    #         f"Speed: {simulation_speed}x [Up/Down]",
    #         f"Paused: {simulation_paused} [Space]",
    #         f"S: {status_counts['S']}",
    #         f"I: {status_counts['I']}",
    #         f"R: {status_counts['R']}",
    #         f"D: {status_counts['D']}"
    #     ]
    #     y = 10
    #     for text in texts:
    #         surf = font.render(text, True, (255,255,255))
    #         screen.blit(surf, (10, y))
    #         y += 20

    # running = True
    # while running:
    #     # Handle input
    #     for event in pygame.event.get():
    #         if event.type == pygame.QUIT:
    #             running = False
    #         elif event.type == pygame.KEYDOWN:
    #             if event.key == pygame.K_SPACE:
    #                 simulation_paused = not simulation_paused
    #             elif event.key == pygame.K_UP:
    #                 simulation_speed = min(5, simulation_speed + 0.5)
    #             elif event.key == pygame.K_DOWN:
    #                 simulation_speed = max(0.1, simulation_speed - 0.5)
        
    #     # Update simulation
    #     if not simulation_paused:
    #         for _ in range(int(simulation_speed)):
    #             simulation_step()
    #             if status_counts["I"] == 0:
    #                 simulation_paused = True

    #     # Update display
    #     screen.fill((30, 30, 30))
    #     draw_edges()
    #     draw_nodes()
    #     draw_ui()
    #     pygame.display.flip()
    #     clock.tick(fps)

    # pygame.quit()