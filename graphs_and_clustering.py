import agent
import random

def create_graph():
    total_population = int(input("Please enter the total number of people: "))
    num_of_agents_in_cluster = 20

    agents = {}

    #creating clusters (nodes inside clusters have a lot of edges among them since they interact with each other a lot)
    for j in range(int(total_population/num_of_agents_in_cluster)):
        for i in range(num_of_agents_in_cluster * j, j * num_of_agents_in_cluster + num_of_agents_in_cluster):
            mobility = random.uniform(0.3,1)
            immunity = random.uniform(0.1, 0.9)
            age = random.randint(0,100)
            agents[i] = agent.Agent(i,age,immunity,mobility,j)
        for k in range(num_of_agents_in_cluster * j, j * num_of_agents_in_cluster + num_of_agents_in_cluster):
            for x in range(num_of_agents_in_cluster * j, j * num_of_agents_in_cluster + num_of_agents_in_cluster):
                if k != x:
                    if random.random() <= 0.10: #prob of having an edge inside cluster is 10%
                        agents[k].neighbours.add(x)
                        agents[x].neighbours.add(k)

    #creating edges among clusters 
    superspreaders= []
    for j in range(int(total_population/num_of_agents_in_cluster)):
        for i in range(num_of_agents_in_cluster * j, j * num_of_agents_in_cluster + num_of_agents_in_cluster):
            if random.random() <= 0.2:#prob of having edge outside of cluster is 20%
                random_num = random.randint(0,int(total_population/num_of_agents_in_cluster)-1)#randomly select a cluster
                while(random_num == j):
                    random_num = random.randint(0,int(total_population/num_of_agents_in_cluster)-1)
                
                for k in range(num_of_agents_in_cluster * random_num, random_num * num_of_agents_in_cluster + num_of_agents_in_cluster):
                    prob = random.random()
                    if prob < 0.05: #prob of having edge outside of cluster with every node in the selected cluster is 5%
                        agents[i].neighbours.add(k)
                        agents[k].neighbours.add(i)
                    # if prob >= 0.5: #prob of having edge outside of cluster is 50%
                    #     break





            # for k in range(total_population):
            #     if k in range(num_of_agents_in_cluster * j, j * num_of_agents_in_cluster + num_of_agents_in_cluster):
            #         continue
            #     else:
            #         if random_num <=3 and not graph.has_edge(i,k): #prob of having edge outside of cluster is 10%
            #             graph.add_edge(i,k)
            #             agents[i].neighbours.append(k)
            #             agents[k].neighbours.append(i)
            #             break


    for i in range(total_population):
        random_num = random.random()
        if random_num < 0.001: #prob of having a superspreader in the population is 0.1%
            superspreaders.append(i)

    # print(superspreaders)
    for i in superspreaders:
            max_connection_limit = 20
            current_connection_count = 0
            for j in range(total_population):
                if i !=j and random.random() <= 0.03: #superspreaders have 3% chance of having an edge with any other node
                    if(current_connection_count>=max_connection_limit): #30 is the maximum number of people that the superspreader can connect to
                        break
                    agents[i].neighbours.add(j)
                    agents[j].neighbours.add(i)
                    current_connection_count+=1

    for i in range(total_population):
        if len(agents[i].neighbours) == 0:
            cluster_id = agents[i].cluster
            cluster_start = cluster_id * num_of_agents_in_cluster
            cluster_end = cluster_start + num_of_agents_in_cluster
            neigbours_to_force_edge_with = []
            for j in range(cluster_start, cluster_end):
                if j != i:
                    neigbours_to_force_edge_with.append(j)
            
            if neigbours_to_force_edge_with:
                random_num = random.choice(neigbours_to_force_edge_with)
                agents[i].neighbours.add(random_num)
                agents[random_num].neighbours.add(i)

    return agents
    # for i in agents.keys():
    #     print(agents[i].id, agents[i].neighbours)