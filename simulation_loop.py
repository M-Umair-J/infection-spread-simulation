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
    step_delay = 500  # milliseconds between steps 
    last_step_time = 0

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
                    step_delay = max(50, step_delay - 50)  # Faster (lower delay)
                elif event.key == pygame.K_DOWN:
                    step_delay = min(2000, step_delay + 50)  # Slower (higher delay)
        current_time = pygame.time.get_ticks()
        if not (simulation_paused):
                #only update if enough time has passed
                if current_time - last_step_time > step_delay / simulation_speed:
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
                    last_step_time = current_time
                
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

        #simulation speed control component
        pygame.draw.rect(screen, (60, 60, 60), (10, height - 40, 200, 30))
        pygame.draw.rect(screen, (100, 100, 100), (10, height - 40, int(step_delay/10), 30))
        text = font.render(f"Simulation Speed: {1000/step_delay:.1f} steps/sec", True, (255, 255, 255))
        screen.blit(text, (15, height - 35))

        pygame.display.flip()
        clock.tick(fps)

    pygame.quit()