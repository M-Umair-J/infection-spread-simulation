# import pygame
# import math
# import random

# pygame.init()


# h = 786
# w = 1024
# screen = pygame.display.set_mode((w,h))
# clock = pygame.time.Clock()
# is_running = True



# # def render_nodes(agents):
# clusters=set({})
# for node in agents.keys():
#     clusters.add(agents[node].cluster)
# c = len(clusters) # number of clusters

# #creating cells for clusters
# cols = math.ceil(math.sqrt(c * w / h))
# rows = math.ceil(c / cols)
# cell_w = w // cols
# cell_h = h // rows
# r_cluster = min(cell_w, cell_h) * 0.4 #setting size of cluster to 40% of the cell size assigned for the cluster
# r_node = max(3, int(r_cluster / math.sqrt(len(agents) / c) / 2)) #propotionate node radius of node inside the cluster
        
#     #calculate each cluster center
# cluster_centers = {}
# for idx, cid in enumerate(clusters):
#     row = idx // cols
#     col = idx % cols
#     cx = col * cell_w + cell_w // 2
#     cy = row * cell_h + cell_h // 2
#     cluster_centers[cid] = (cx, cy)
    
# for cid in clusters:
#     members = [a for a in agents.values() if a.cluster == cid]
#     M = len(members)
#     if M == 0: continue
#     delta = 2 * math.pi / M
#     cx, cy = cluster_centers[cid]
#     for i, ag in enumerate(members):
#         theta = i * delta
#         # for a filled‐circle effect, randomize radius
#         rr = random.uniform(0.3 * r_cluster, r_cluster)
#         x = cx + rr * math.cos(theta)
#         y = cy + rr * math.sin(theta)
#         ag.pos = (int(x), int(y))

# def draw_edges(surface, agents, color=(150,150,150)):
#     for ag in agents.values():
#         for nb in ag.neighbours:
#             # draw each edge only once
#             if ag.id < nb:
#                 pygame.draw.line(surface, color, ag.pos, agents[nb].pos, 1)

# def draw_nodes(surface, agents):
#     for ag in agents.values():
#         # pick color by status if you like, here all green
#         pygame.draw.circle(surface, (0,200,0), ag.pos, r_node)


# def draw_comp(agents):
#     running = True
#     while running:
#         for ev in pygame.event.get():
#             if ev.type == pygame.QUIT:
#                 running = False

#         screen.fill((30,30,30))
#         draw_edges(screen, agents)
#         draw_nodes(screen, agents)

#         pygame.display.flip()
#         clock.tick(60)

# pygame.quit()

#     # def render_edges(agents):


# # def draw_components(agents):

# #     while is_running:
# #         for event in pygame.event.get():
# #             if event.type == pygame.QUIT:
# #                 is_running == False
        
# #         pygame.display.flip()
# #         clock.tick(90)
# #     pygame.quit()



import pygame
import math
import random

def run_visualization(agents, width=1024, height=786, fps=60):
    pygame.init()
    screen = pygame.display.set_mode((width, height))
    clock  = pygame.time.Clock()

    
    clusters = sorted({ag.cluster for ag in agents.values()})
    C = len(clusters)

    
    cols = math.ceil(math.sqrt(C * width / height))
    rows = math.ceil(C / cols)
    cell_w = width  // cols
    cell_h = height // rows

    
    r_cluster = min(cell_w, cell_h) * 0.4
    avg_per_cluster = len(agents) / C if C>0 else 1
    r_node = max(3, int(r_cluster / math.sqrt(avg_per_cluster) / 2))

    
    cluster_centers = {}
    for idx, cid in enumerate(clusters):
        row = idx // cols
        col = idx % cols
        cx = col * cell_w + cell_w // 2
        cy = row * cell_h + cell_h // 2
        cluster_centers[cid] = (cx, cy)

    
    for cid in clusters:
        members = [ag for ag in agents.values() if ag.cluster == cid]
        M = len(members)
        if M == 0:
            continue
        delta = 2 * math.pi / M
        cx, cy = cluster_centers[cid]
        for i, ag in enumerate(members):
            theta = i * delta
            rr = random.uniform(0.3 * r_cluster, r_cluster)
            x = cx + rr * math.cos(theta)
            y = cy + rr * math.sin(theta)
            ag.pos = (int(x), int(y))

    
    def draw_edges():
        for ag in agents.values():
            for nb in ag.neighbours:
                if ag.id < nb:
                    pygame.draw.line(screen, (150,150,150), ag.pos, agents[nb].pos, 1)

    def draw_nodes():
        for ag in agents.values():
            pygame.draw.circle(screen, (0,200,0), ag.pos, r_node)

    
    running = True
    while running:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False

        screen.fill((30,30,30))
        draw_edges()
        draw_nodes()

        pygame.display.flip()
        clock.tick(fps)

    pygame.quit()
