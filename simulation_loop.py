import pygame
import random
import networkx as nx
import matplotlib.pyplot as plt
import multiprocessing
from multiprocessing import Queue
import numpy as np
import platform

# Define the plotting process function
def run_plot_process(data_queue):
    """Run the plotting process separately from the main simulation"""
    import matplotlib
    
    # Use a better backend for macOS
    if platform.system() == 'Darwin':  # macOS
        matplotlib.use('MacOSX')  # Better for Mac
    else:
        matplotlib.use('TkAgg')  # Use TkAgg for other platforms
        
    import matplotlib.pyplot as plt
    
    # Set up the figure
    plt.ion()  # Interactive mode
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111)
    
    # Initial empty data
    time_points = [0]
    susceptible_data = [0]
    infected_data = [0]
    recovered_data = [0]
    dead_data = [0]
    
    # Initial plot lines
    s_line, = ax.plot(time_points, susceptible_data, 'g-', label='Susceptible')
    i_line, = ax.plot(time_points, infected_data, 'r-', label='Infected')
    r_line, = ax.plot(time_points, recovered_data, 'b-', label='Recovered')
    d_line, = ax.plot(time_points, dead_data, 'k-', label='Dead')
    
    ax.set_xlabel('Time')
    ax.set_ylabel('Population')
    ax.set_title('Disease Progression')
    ax.legend()
    
    plt.show(block=False)
    print("Plot window should be visible now")
    
    # Main loop to receive data
    running = True
    while running:
        try:
            # Get new data with timeout
            message = data_queue.get(timeout=0.1)
            
            if message[0] == "update":
                # Unpack data
                _, t_data, s_data, i_data, r_data, d_data = message
                
                # Update data
                time_points = t_data
                susceptible_data = s_data
                infected_data = i_data
                recovered_data = r_data
                dead_data = d_data
                
                # Update plot lines
                s_line.set_data(time_points, susceptible_data)
                i_line.set_data(time_points, infected_data)
                r_line.set_data(time_points, recovered_data)
                d_line.set_data(time_points, dead_data)
                
                # Rescale axes
                ax.relim()
                ax.autoscale_view()
                
                # Redraw
                fig.canvas.draw_idle()
                fig.canvas.flush_events()
                
            elif message[0] == "close":
                running = False
                
        except Exception as e:
            # Just continue if no new data or other error
            pass
            
        # Check if figure still exists
        if not plt.fignum_exists(fig.number):
            running = False
    
    plt.close(fig)

def run_visualization(agents, width=1024, height=768, fps=60):
    # Set multiprocessing start method to spawn for all platforms, especially important for macOS
    if platform.system() == 'Darwin' and multiprocessing.get_start_method() != 'spawn':
        try:
            multiprocessing.set_start_method('spawn', force=True)
        except RuntimeError:
            # If already set and we can't force, at least we tried
            pass
            
    number_of_nodes = len(agents)
    # Initialize pygame
    pygame.init()
    
    # Get the current screen info for a large window
    screen_info = pygame.display.Info()
    width, height = screen_info.current_w - 100, screen_info.current_h - 100  # Slightly smaller than screen
    
    # Create a resizable window (will have minimize/maximize buttons)
    pygame.display.set_caption("Infection Spread Simulation")
    screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
    
    clock = pygame.time.Clock()
    font = pygame.font.SysFont('Arial', 16)

    # Parameters for simulation
    initial_infection_rate = 0.05
    min_recovery_time = 10
    max_recovery_time = 16
    mortality_rate = 0.01
    time_step = 0
    simulation_paused = False
    zoom_level = 1.0
    simulation_speed = 1
    step_delay = 500  # milliseconds between steps 
    last_step_time = 0
    
    # Create a queue for inter-process communication
    plot_queue = Queue()
    
    # Start as None, we'll create when user clicks button
    plot_process = None
    plot_window_open = False

    # Initialize infections
    num_initial_infected = int(len(agents) * initial_infection_rate)
    initial_infected = random.sample(list(agents.keys()), num_initial_infected)
    
    # Keeping track of status
    status_counts = {
        "S": len(agents) - num_initial_infected,
        "I": num_initial_infected,
        "R": 0,
        "D": 0
    }

    # Data tracking for plot
    time_points = [0]
    susceptible_data = [status_counts["S"]]
    infected_data = [status_counts["I"]]
    recovered_data = [status_counts["R"]]
    dead_data = [status_counts["D"]]

    # Function to open plot in separate process
    def open_plot_window():
        nonlocal plot_process, plot_window_open
        
        # Don't start if already running
        if plot_process is not None and plot_process.is_alive():
            return
            
        try:
            # Create and start process
            plot_process = multiprocessing.Process(target=run_plot_process, args=(plot_queue,))
            plot_process.daemon = True
            plot_process.start()
            plot_window_open = True
            
            # Send initial data
            plot_queue.put(("update", time_points, susceptible_data, infected_data, recovered_data, dead_data))
        except Exception as e:
            print(f"Error starting plot process: {e}")
            plot_window_open = False
    
    # Function to draw a button
    def draw_button(text, x, y, width, height):
        button_rect = pygame.Rect(x, y, width, height)
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]
        
        # Check if mouse is over button
        hovered = button_rect.collidepoint(mouse_pos)
        
        # Draw button with different color when hovered
        color = (100, 100, 150) if hovered else (70, 70, 120)
        pygame.draw.rect(screen, color, button_rect)
        pygame.draw.rect(screen, (150, 150, 200), button_rect, 2)  # Border
        
        # Draw text
        text_surf = font.render(text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=button_rect.center)
        screen.blit(text_surf, text_rect)
        
        # Return both the hover state and the button rect as a tuple
        return (hovered and mouse_clicked, button_rect)

    # Your existing zoom function
    def zoom_at_mouse(mouse_x, mouse_y, zoom_delta):
        nonlocal zoom_level
        old_zoom = zoom_level
        zoom_level += zoom_delta
        
        # Limiting zoom level
        zoom_level = max(0.2, min(8.0, zoom_level))
        
        # Calculating zoom factor
        zoom_factor = zoom_level / old_zoom
        
        # Updating positions centered around mouse pointer
        for agent_id in list(agents.keys()):
            if agent_id in agents:
                # Get current position
                current_pos = agents[agent_id].pos
                
                # Calculate vector from mouse to agent
                dx = current_pos[0] - mouse_x
                dy = current_pos[1] - mouse_y
                
                # Scale vector by zoom factor
                new_dx = dx * zoom_factor
                new_dy = dy * zoom_factor
                
                # Calculate new position
                new_x = mouse_x + new_dx
                new_y = mouse_y + new_dy
                
                # Update agent position
                agents[agent_id].pos = (new_x, new_y)

    # Function to find agent under mouse cursor
    def get_agent_under_cursor(mouse_pos):
        for agent_id, agent in agents.items():
            # Calculate distance from mouse to agent center
            distance = ((agent.pos[0] - mouse_pos[0])**2 + (agent.pos[1] - mouse_pos[1])**2)**0.5
            # Check if mouse is within the agent's circle
            if distance <= max(1, int(1 * zoom_level)):  # Changed from 3 to 2
                return agent
        return None

    # Initialize agents with infection
    for nodes in initial_infected:
        agents[nodes].infect(0)

    # Create NetworkX graph (to visualize the population)
    G = nx.Graph()
    for agent_id, agent_obj in agents.items():
        G.add_node(agent_id, cluster=agent_obj.cluster)
        for neighbor in agent_obj.neighbours:
            G.add_edge(agent_id, neighbor)

    # Calculating initial layout
    positions = nx.spring_layout(G, iterations=50)
    max_x = max(pos[0] for pos in positions.values()) or 1
    min_x = min(pos[0] for pos in positions.values()) or 0
    max_y = max(pos[1] for pos in positions.values()) or 1
    min_y = min(pos[1] for pos in positions.values()) or 0

    # Storing base positions
    base_positions = {}
    for agent_id, pos in positions.items():
        scaled_x = (pos[0] - min_x) / (max_x - min_x) * (width - 100) + 50
        scaled_y = (pos[1] - min_y) / (max_y - min_y) * (height - 100) + 50
        base_positions[agent_id] = (scaled_x, scaled_y)
        agents[agent_id].pos = (scaled_x, scaled_y)
    
    # Initialize button state variables
    show_graph_button_rect = None

    # Main simulation loop
    running = True
    clicked = False
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
                elif event.key == pygame.K_ESCAPE:
                    running = False  # Exit on ESC key
            elif event.type == pygame.VIDEORESIZE:
                # Handle window resize
                width, height = event.size
                screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
            elif event.type == pygame.MOUSEWHEEL:
                # Handle zoom with mouse wheel
                mouse_x, mouse_y = pygame.mouse.get_pos()
                zoom_delta = event.y * 0.1  # Adjust sensitivity
                zoom_at_mouse(mouse_x, mouse_y, zoom_delta)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    if show_graph_button_rect and show_graph_button_rect.collidepoint(event.pos):
                        print("Button clicked - opening plot")
                        if not plot_window_open:
                            open_plot_window()
                clicked = True
            elif event.type == pygame.MOUSEBUTTONUP:
                clicked = False
        
        current_time = pygame.time.get_ticks()
        if not simulation_paused:
            # Only update if enough time has passed
            if current_time - last_step_time > step_delay / simulation_speed:
                new_infections = []
                # Handling infections
                for agent in agents.values():
                    if agent.status == "I":
                        # Attempt to infect
                        for neighbour_id in agent.decide_to_infect_neighbours():
                            if neighbour_id in agents and agents[neighbour_id].status == "S":
                                if agent.attempt_to_infect_neighbour(agents[neighbour_id], time_step):
                                    new_infections.append(neighbour_id)
                status_counts["S"] -= len(new_infections)
                status_counts["I"] += len(new_infections)

                # Handling deaths and recovery
                for agent in agents.values():
                    previous_status = agent.status
                    if agent.status == "I" and (time_step - agent.last_infected_timestep) >= agent.recovery_time:
                        # Use the agent's individual recovery time instead of the global one
                        if random.random() < mortality_rate:
                            agent.status = "D"
                        else:
                            agent.status = "R"
                        
                        if agent.status != previous_status:
                            status_counts[previous_status] -= 1
                            status_counts[agent.status] += 1
                            if agent.status == "D":  # Removing dead nodes from simulation
                                if agent.id in base_positions:
                                    del base_positions[agent.id]
                
                # Update time step and last update time
                time_step += 1
                last_step_time = current_time
                
                # Collect data for plot every 5 steps
                if time_step % 5 == 0:
                    time_points.append(time_step)
                    susceptible_data.append(status_counts["S"])
                    infected_data.append(status_counts["I"])
                    recovered_data.append(status_counts["R"])
                    dead_data.append(status_counts["D"])
                    
                    # Send update if process is running
                    if plot_window_open and plot_process is not None and plot_process.is_alive():
                        try:
                            plot_queue.put(("update", time_points, susceptible_data, infected_data, recovered_data, dead_data))
                        except:
                            pass
        
        # Drawing directly in main loop
        screen.fill((30, 30, 30))
        
        # Drawing edges
        for agent in list(agents.values()):
            if agent.status == "D":
                del agents[agent.id]
                continue
            for nid in agent.neighbours:
                if nid > agent.id and nid in agents and agents[nid].status != "D":  # Avoid duplicates
                    pygame.draw.aaline(screen, (150,150,150), 
                                     (int(agent.pos[0]), int(agent.pos[1])),
                                     (int(agents[nid].pos[0]), int(agents[nid].pos[1])))

        # Drawing nodes
        for agent in agents.values():
            color = (
                (40,40,40) if agent.status == "D" else
                (200,0,0) if agent.status == "I" else
                (0,0,200) if agent.status == "R" else
                (0,200,0)
            )
            pygame.draw.circle(screen, color, 
                 (int(agent.pos[0]), int(agent.pos[1])), 
                 max(1, int(1 * zoom_level)))  # Changed from 3 to 2
        
        # Check for agent under mouse cursor and display info
        mouse_pos = pygame.mouse.get_pos()
        hovered_agent = get_agent_under_cursor(mouse_pos)
        if hovered_agent:
            # Prepare info texts
            info_texts = [
                f"Agent ID: {hovered_agent.id}",
                f"Status: {hovered_agent.status}",
                f"Connections: {len(hovered_agent.neighbours)}",
                f"Cluster: {hovered_agent.cluster}",
                f"Recovery Time: {hovered_agent.recovery_time} days"
            ]
            
            # Display infection time if infected
            if hovered_agent.status == "I" and hasattr(hovered_agent, 'last_infected_timestep'):
                days_infected = time_step - hovered_agent.last_infected_timestep
                days_left = hovered_agent.recovery_time - days_infected
                info_texts.append(f"Days Infected: {days_infected}")
                info_texts.append(f"Days Until Recovery: {days_left}")
            
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
            
            # Render all info texts
            y_offset = 0
            for info in info_texts:
                text_surf = font.render(info, True, (255, 255, 255))
                screen.blit(text_surf, (panel_x + 10, panel_y + 10 + y_offset))
                y_offset += line_height
                
            # Highlight the hovered agent
            highlight_radius = max(2, int(2 * zoom_level))  # Changed from 4 to 3
            pygame.draw.circle(screen, (255, 255, 255), 
                             (int(hovered_agent.pos[0]), int(hovered_agent.pos[1])), 
                             highlight_radius, 2)  # Draw white outline
        
        # Draw "Show Graph" button
        button_x = width - 150
        button_y = height - 50
        show_graph_hovered, show_graph_button_rect = draw_button("Show Graph", button_x, button_y, 130, 40)

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
        help_panel_x = width - 270  # Position from right edge
        help_panel_y = 10           # Position from top edge
        help_panel_width = 250
        help_panel_height = 100     # Increased height to fit all controls
        
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
            "Mouse Wheel - Zoom In/Out",
            "ESC - Exit"
        ]
        
        y = help_panel_y + 10
        for text in help_texts:
            screen.blit(font.render(text, True, (200, 200, 200)), 
                       (help_panel_x + 10, y))
            y += 17
        
        # Simulation speed control component - improved layout
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
        text_width, text_height = text_surf.get_size()
        text_x = speed_bar_x + (speed_bar_width - text_width) // 2
        text_y = speed_bar_y + (speed_bar_height - text_height) // 2
        
        # Draw text
        screen.blit(text_surf, (text_x, text_y))
        
        pygame.display.flip()
        clock.tick(fps)

    # Clean up before exiting
    if plot_process is not None and plot_process.is_alive():
        try:
            plot_queue.put(("close",))
            plot_process.join(timeout=1.0)
            if plot_process.is_alive():
                plot_process.terminate()
        except:
            pass
    
    pygame.quit()

if __name__ == "__main__":
    # Set start method to spawn for better compatibility
    multiprocessing.set_start_method('spawn', force=True)