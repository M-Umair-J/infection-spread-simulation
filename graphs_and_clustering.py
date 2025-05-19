import agent
import random

def create_graph():
    total_population = int(input("Please enter the total number of people: "))
    num_of_agents_in_cluster = 20

    agents = {}
    full_clusters = total_population // num_of_agents_in_cluster
    remainder = total_population % num_of_agents_in_cluster

    #creating clusters (nodes inside clusters have a lot of edges among them since they interact with each other a lot)
    for j in range(full_clusters):
        for i in range(num_of_agents_in_cluster * j, j * num_of_agents_in_cluster + num_of_agents_in_cluster):
            mobility = random.uniform(0.3,1)
            immunity = random.uniform(0.1, 0.6)
            age = random.randint(0,100)
            agents[i] = agent.Agent(i,age,immunity,mobility,j)
        for k in range(num_of_agents_in_cluster * j, j * num_of_agents_in_cluster + num_of_agents_in_cluster):
            for x in range(num_of_agents_in_cluster * j, j * num_of_agents_in_cluster + num_of_agents_in_cluster):
                if k != x:
                    if random.random() <= 0.10: #prob of having an edge inside cluster is 10%
                        agents[k].neighbours.add(x)
                        agents[x].neighbours.add(k)
    
    # Handle remainder agents - assign them to the final cluster
    if remainder > 0:
        final_cluster = full_clusters
        start_idx = full_clusters * num_of_agents_in_cluster
        
        # Create remainder agents
        for i in range(start_idx, total_population):
            mobility = random.uniform(0.3,1)
            immunity = random.uniform(0.1, 0.6)
            age = random.randint(0,100)
            agents[i] = agent.Agent(i,age,immunity,mobility,final_cluster)
        
        # Connect remainder agents within their cluster
        for k in range(start_idx, total_population):
            for x in range(start_idx, total_population):
                if k != x:
                    if random.random() <= 0.10: #prob of having an edge inside cluster is 10%
                        agents[k].neighbours.add(x)
                        agents[x].neighbours.add(k)
        
        # Ensure remainder agents connect to the main network
        if full_clusters > 0:
            # Connect the remainder cluster to at least one other cluster
            random_agent_from_remainder = random.randint(start_idx, total_population-1)
            random_cluster = random.randint(0, full_clusters-1)
            random_agent_from_other = random.randint(random_cluster*num_of_agents_in_cluster, 
                                                    (random_cluster+1)*num_of_agents_in_cluster-1)
            
            agents[random_agent_from_remainder].neighbours.add(random_agent_from_other)
            agents[random_agent_from_other].neighbours.add(random_agent_from_remainder)

    #creating edges among clusters 
    superspreaders= []
    actual_clusters = full_clusters + (1 if remainder > 0 else 0)
    
    for j in range(actual_clusters):
        cluster_start = j * num_of_agents_in_cluster
        cluster_end = min(total_population, (j+1) * num_of_agents_in_cluster)
        
        for i in range(cluster_start, cluster_end):
            if random.random() <= 0.2: #prob of having edge outside of cluster is 20%
                # Pick a different cluster
                random_num = random.randint(0, actual_clusters-1)
                while random_num == j:
                    random_num = random.randint(0, actual_clusters-1)
                
                target_start = random_num * num_of_agents_in_cluster
                target_end = min(total_population, (random_num+1) * num_of_agents_in_cluster)
                
                for k in range(target_start, target_end):
                    prob = random.random()
                    if prob < 0.05: #prob of having edge outside of cluster with every node in the selected cluster is 5%
                        agents[i].neighbours.add(k)
                        agents[k].neighbours.add(i)

    for i in range(total_population):
        random_num = random.random()
        if random_num < 0.001: #prob of having a superspreader in the population is 0.1%
            superspreaders.append(i)

    for i in superspreaders:
        max_connection_limit = 20
        current_connection_count = 0
        for j in range(total_population):
            if i != j and random.random() <= 0.03: #superspreaders have 3% chance of having an edge with any other node
                if(current_connection_count >= max_connection_limit): #20 is the maximum number of people that the superspreader can connect to
                    break
                agents[i].neighbours.add(j)
                agents[j].neighbours.add(i)
                current_connection_count += 1

    # Ensure no isolated agents
    for i in range(total_population):
        if len(agents[i].neighbours) == 0:
            # Find this agent's cluster
            cluster_id = agents[i].cluster
            cluster_start = cluster_id * num_of_agents_in_cluster
            cluster_end = min(total_population, (cluster_id+1) * num_of_agents_in_cluster)
            
            # If no neighbors in own cluster, connect to a random agent
            potential_neighbors = list(range(cluster_start, cluster_end))
            potential_neighbors.remove(i)  # Don't connect to self
            
            if potential_neighbors:
                # Connect to someone in the same cluster
                random_neighbor = random.choice(potential_neighbors)
                agents[i].neighbours.add(random_neighbor)
                agents[random_neighbor].neighbours.add(i)
            else:
                # If somehow still no neighbors, connect to any random agent
                random_neighbor = random.randint(0, total_population-1)
                while random_neighbor == i:
                    random_neighbor = random.randint(0, total_population-1)
                agents[i].neighbours.add(random_neighbor)
                agents[random_neighbor].neighbours.add(i)
    
    # Final check to ensure the graph is connected
    # Build adjacency list for a simple connectivity check
    adj_list = {i: [] for i in range(total_population)}
    for i in range(total_population):
        for neighbor in agents[i].neighbours:
            adj_list[i].append(neighbor)
    
    # Iterative DFS to check connectivity (avoids recursion error)
    visited = [False] * total_population
    
    def check_connectivity():
        if total_population == 0:
            return
            
        stack = [0]  # Start from first node
        visited[0] = True
        
        while stack:
            current = stack.pop()
            for neighbor in adj_list[current]:
                if not visited[neighbor]:
                    visited[neighbor] = True
                    stack.append(neighbor)
    
    check_connectivity()  # Run the connectivity check
    
    # If there are still unvisited nodes, connect them to the main component
    for i in range(total_population):
        if not visited[i]:
            # Connect to any visited node
            connected_nodes = [j for j in range(total_population) if visited[j]]
            if connected_nodes:  # Check if there are any connected nodes
                random_visited = random.choice(connected_nodes)
                agents[i].neighbours.add(random_visited)
                agents[random_visited].neighbours.add(i)
                # Mark as visited
                visited[i] = True

    return agents
    # for i in agents.keys():
    #     print(agents[i].id, agents[i].neighbours)