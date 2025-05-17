import pygame
import math
import random
import networkx as nx

def run_visualization(agents, width=1024, height=786, fps=60):
    pygame.init()
    screen = pygame.display.set_mode((width, height))
    clock = pygame.time.Clock()
    
    # Define node radius
    r_node = 5  # You can adjust this value as needed
    
    # Create NetworkX graph from your agent structure - simplified edge creation
    G = nx.Graph()  # Using Graph instead of DiGraph ensures edges are unique
    
    for agent_id, agent_obj in agents.items():
        G.add_node(agent_id, cluster=agent_obj.cluster)
    
    for agent_id, agent_obj in agents.items():
        for neighbor in agent_obj.neighbours:
            G.add_edge(agent_id, neighbor)  # NetworkX Graph automatically handles duplicates
            
    
    # Apply force-directed layout (spring layout)
    positions = nx.spring_layout(G, iterations=100)
    
    # Scale positions to fit screen dimensions
    max_x = max(pos[0] for pos in positions.values())
    min_x = min(pos[0] for pos in positions.values())
    max_y = max(pos[1] for pos in positions.values())
    min_y = min(pos[1] for pos in positions.values())
    
    # Store base positions
    base_positions = {}
    for agent_id, pos in positions.items():
        scaled_x = (pos[0] - min_x) / (max_x - min_x) * (width - 100) + 50
        scaled_y = (pos[1] - min_y) / (max_y - min_y) * (height - 100) + 50
        base_positions[agent_id] = (scaled_x, scaled_y)
        agents[agent_id].pos = (int(scaled_x), int(scaled_y))
    
    # Zoom and pan variables
    zoom_level = 1.0
    
    # Update positions based on zoom level and mouse position
    def update_agent_positions(mouse_x, mouse_y, zoom_delta):
        nonlocal zoom_level
        old_zoom = zoom_level
        zoom_level += zoom_delta
        
        # Limit zoom level
        if zoom_level < 0.2:
            zoom_level = 0.2
        elif zoom_level > 10.0:
            zoom_level = 10.0
            
        # Calculate zoom factor
        zoom_factor = zoom_level / old_zoom
        
        for agent_id, base_pos in base_positions.items():
            # Get current position
            current_pos = agents[agent_id].pos
            
            # Calculate new position zoomed around mouse pointer
            dx = current_pos[0] - mouse_x
            dy = current_pos[1] - mouse_y
            
            new_x = mouse_x + dx * zoom_factor
            new_y = mouse_y + dy * zoom_factor
            
            # Update agent position
            agents[agent_id].pos = (int(new_x), int(new_y))
    
    # Draw functions
    def draw_edges():
        for u, v in G.edges():
            pygame.draw.aaline(screen, (150,150,150), agents[u].pos, agents[v].pos)

    def draw_nodes():
        for ag in agents.values():
            # Color nodes based on status
            if hasattr(ag, 'status'):
                if ag.status == "S":  # Susceptible
                    color = (0, 200, 0)  # Green
                elif ag.status == "I":  # Infected
                    color = (200, 0, 0)  # Red
                elif ag.status == "R":  # Recovered
                    color = (0, 0, 200)  # Blue
                else:
                    color = (200, 200, 0)  # Yellow for unknown
            else:
                color = (0, 200, 0)  # Default green
            
            # Adjust node size with zoom
            node_radius = int(r_node * zoom_level)
            if node_radius < 1:
                node_radius = 1
                
            pygame.draw.circle(screen, color, ag.pos, node_radius)
    
    # Draw instructions
    font = pygame.font.SysFont('Arial', 16)
    def draw_instructions():
        instructions = [
            "Mouse Wheel: Zoom In/Out",
            f"Zoom Level: {zoom_level:.2f}x"
        ]
        
        for i, text in enumerate(instructions):
            text_surf = font.render(text, True, (255, 255, 255))
            screen.blit(text_surf, (10, 10 + i * 20))
    
    running = True
    while running:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
            elif ev.type == pygame.MOUSEWHEEL:
                # Get mouse position
                mouse_x, mouse_y = pygame.mouse.get_pos()
                
                # Calculate zoom delta
                zoom_delta = 0.1 * ev.y  # ev.y is positive when scrolling up
                
                # Update positions with new zoom level centered on mouse
                update_agent_positions(mouse_x, mouse_y, zoom_delta)

        screen.fill((30,30,30))
        draw_edges()
        draw_nodes()
        draw_instructions()

        pygame.display.flip()
        clock.tick(fps)

    pygame.quit()
