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
    




    #function for zooming mouse pointer
    def zoom_at_mouse(mouse_x, mouse_y, zoom_delta):
        nonlocal zoom_level
        old_zoom = zoom_level
        zoom_level += zoom_delta
        
        #limiting zoom level
        zoom_level = max(0.2, min(5.0, zoom_level))
        
        #dalculating zoom factor
        zoom_factor = zoom_level / old_zoom
        
        #updating positions centered around mouse pointer
        for agent_id in list(agents.keys()):
            if agent_id in agents:
                #get current position
                current_pos = agents[agent_id].pos

                #calculating vector from mouse to agent
                dx = current_pos[0] - mouse_x
                dy = current_pos[1] - mouse_y
                
                #scaling vector by zoom factor
                new_dx = dx * zoom_factor
                new_dy = dy * zoom_factor
                
                #calculating new position
                new_x = mouse_x + new_dx
                new_y = mouse_y + new_dy
                
                #updating agent position
                agents[agent_id].pos = (new_x, new_y)



    #function to find agent under mouse cursor
    def get_agent_under_cursor(mouse_pos):
        for agent_id, agent in agents.items():
            #calculate distance from mouse to agent center
            distance = ((agent.pos[0] - mouse_pos[0])**2 + (agent.pos[1] - mouse_pos[1])**2)**0.5
            #check if mouse is within the agent's circle
            if distance <= max(1, int(5 * zoom_level)):
                return agent
        return None








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
            elif event.type == pygame.MOUSEWHEEL:
                #handle zoom with mouse wheel
                mouse_x, mouse_y = pygame.mouse.get_pos()
                zoom_delta = event.y * 0.1  #adjust sensitivity
                zoom_at_mouse(mouse_x, mouse_y, zoom_delta)
        
        
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
       
        # Drawing UI with better layout
        info_panel_x = 10
        info_panel_y = 10
        info_panel_width = 150
        info_panel_height = 160

        # Semi-transparent background for status panel
        status_panel = pygame.Surface((info_panel_width, info_panel_height), pygame.SRCALPHA)
        status_panel.fill((0, 0, 0, 150))  # Black with opacity
        screen.blit(status_panel, (info_panel_x, info_panel_y))

        # Draw border
        pygame.draw.rect(screen, (150, 150, 150), (info_panel_x, info_panel_y, info_panel_width, info_panel_height), 1)

        # Status titles
        y = info_panel_y + 10
        titles = ["Simulation Status:", f"Time: {time_step}", f"Zoom: {zoom_level:.2f}x"]
        if simulation_paused:
            titles.append("PAUSED")

        for text in titles:
            screen.blit(font.render(text, True, (255, 255, 255)), (info_panel_x + 10, y))
            y += 20

        # Add a separator line
        pygame.draw.line(screen, (150, 150, 150), 
                        (info_panel_x + 10, y), 
                        (info_panel_x + info_panel_width - 10, y), 1)
        y += 10

        # Status counts with color indicators
        status_texts = {
            "S": "Susceptible",
            "I": "Infected",
            "R": "Recovered",
            "D": "Dead"
        }
        status_colors = {
            "S": (0, 200, 0),    # Green
            "I": (200, 0, 0),    # Red
            "R": (0, 0, 200),    # Blue
            "D": (100, 100, 100) # Gray
        }

        for status, count in status_counts.items():
            # Draw color indicator box
            pygame.draw.rect(screen, status_colors[status], 
                            (info_panel_x + 10, y, 10, 10))
            
            # Draw status text
            status_text = f"{status_texts[status]}: {count}"
            screen.blit(font.render(status_text, True, (255, 255, 255)), 
                       (info_panel_x + 25, y - 2))
            y += 20

        # Draw controls help in the top-right corner
        help_panel_x = width - 260  # Position from right edge
        help_panel_y = 10           # Position from top edge
        help_panel_width = 250
        help_panel_height = 70

        # Background
        help_panel = pygame.Surface((help_panel_width, help_panel_height), pygame.SRCALPHA)
        help_panel.fill((0, 0, 0, 150))  # Semi-transparent black
        screen.blit(help_panel, (help_panel_x, help_panel_y))

        # Border
        pygame.draw.rect(screen, (150, 150, 150), 
                       (help_panel_x, help_panel_y, help_panel_width, help_panel_height), 1)

        # Help text
        help_texts = [
            "Controls:",
            "Space - Pause/Resume",
            "Up/Down - Adjust Speed",
            "Mouse Wheel - Zoom In/Out"
        ]

        y = help_panel_y + 10
        for text in help_texts:
            screen.blit(font.render(text, True, (200, 200, 200)), 
                       (help_panel_x + 10, y))
            y += 15

        # Add a visual indicator for paused state
        if simulation_paused:
            pause_font = pygame.font.SysFont('Arial', 48)
            pause_text = pause_font.render("PAUSED", True, (255, 255, 255))
            
            # Get text dimensions
            text_width, text_height = pause_text.get_size()
            
            # Position text at the center of the screen with transparency
            pause_overlay = pygame.Surface((text_width + 40, text_height + 20), pygame.SRCALPHA)
            pause_overlay.fill((0, 0, 0, 150))
            
            overlay_x = (width - text_width - 40) // 2
            overlay_y = (height - text_height - 20) // 2
            
            screen.blit(pause_overlay, (overlay_x, overlay_y))
            screen.blit(pause_text, (overlay_x + 20, overlay_y + 10))


        #simulation speed control component
        speed_bar_width = 200
        speed_bar_height = 30
        speed_bar_x = 10
        speed_bar_y = height - 40

        # Draw background bar
        pygame.draw.rect(screen, (60, 60, 60), (speed_bar_x, speed_bar_y, speed_bar_width, speed_bar_height))

        # Draw indicator (limit to bar width)
        indicator_width = min(speed_bar_width, int(step_delay/10))
        pygame.draw.rect(screen, (100, 100, 100), (speed_bar_x, speed_bar_y, indicator_width, speed_bar_height))

        # Create speed text
        speed_text = f"Speed: {1000/step_delay:.1f} steps/sec"
        text_surf = font.render(speed_text, True, (255, 255, 255))

        # Position text centered in the bar
        text_width, text_height = font.size(speed_text)
        text_x = speed_bar_x + (speed_bar_width - text_width) // 2
        text_y = speed_bar_y + (speed_bar_height - text_height) // 2

        # Draw text
        screen.blit(text_surf, (text_x, text_y))

        # Check for agent under mouse cursor and display info
        mouse_pos = pygame.mouse.get_pos()
        hovered_agent = get_agent_under_cursor(mouse_pos)
        if hovered_agent:
            # Prepare info texts first to calculate required height
            info_texts = [
                f"Agent ID: {hovered_agent.id}",
                f"Status: {hovered_agent.status}",
                f"Connections: {len(hovered_agent.neighbours)}",
                f"Cluster: {hovered_agent.cluster}"
            ]
            
            # Add additional agent info if those attributes exist
            if hasattr(hovered_agent, 'age'):
                info_texts.append(f"Age: {hovered_agent.age}")
                
            if hasattr(hovered_agent, 'immunity'):
                info_texts.append(f"Immunity: {hovered_agent.immunity:.2f}")
                
            if hasattr(hovered_agent, 'mobility'):
                info_texts.append(f"Mobility: {hovered_agent.mobility:.2f}")
            
            # Display infection time if infected or recovered
            if hovered_agent.status in ["I", "R"] and hasattr(hovered_agent, 'last_infected_timestep'):
                days_infected = time_step - hovered_agent.last_infected_timestep
                info_texts.append(f"Days infected: {days_infected}")
            
            # Calculate dynamic height based on content
            line_height = 20
            padding = 20  # Top and bottom padding
            info_width = 200
            info_height = len(info_texts) * line_height + padding
            
            # Position panel near mouse but keep within screen boundaries
            panel_x = min(width - info_width - 10, mouse_pos[0] + 10)
            panel_y = min(height - info_height - 10, mouse_pos[1] + 10)
            
            # Draw semi-transparent background
            s = pygame.Surface((info_width, info_height), pygame.SRCALPHA)
            s.fill((0, 0, 0, 180))  # Black with 70% opacity
            screen.blit(s, (panel_x, panel_y))
            
            # Draw border
            pygame.draw.rect(screen, (200, 200, 200), (panel_x, panel_y, info_width, info_height), 1)
            
            #draw agent info
            y_offset = 0
            
            #render all info texts
            for info in info_texts:
                text_surf = font.render(info, True, (255, 255, 255))
                screen.blit(text_surf, (panel_x + 10, panel_y + 10 + y_offset))
                y_offset += 20
                
            #highlight the hovered agent
            highlight_radius = max(2, int(6 * zoom_level))
            pygame.draw.circle(screen, (255, 255, 255), 
                             (int(hovered_agent.pos[0]), int(hovered_agent.pos[1])), 
                             highlight_radius, 2)  #draw white outline






        pygame.display.flip()
        clock.tick(fps)

    pygame.quit()