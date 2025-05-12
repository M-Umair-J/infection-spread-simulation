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
            immunity = 0.1
            age = random.randint(0,100)
            agents[i] = agent.Agent(i,age,immunity,mobility,j)
        for k in range(num_of_agents_in_cluster * j, j * num_of_agents_in_cluster + num_of_agents_in_cluster):
            for x in range(num_of_agents_in_cluster * j, j * num_of_agents_in_cluster + num_of_agents_in_cluster):
                random_num = random.randint(1,10)
                if k != x:
                    if random_num <= 8 and not (k in agents[x].neighbours): #prob of having an edge inside cluster is 80%
                        agents[k].neighbours.append(x)
                        agents[x].neighbours.append(k)

    #creating edges among clusters 
    superspreaders= []
    for j in range(int(total_population/num_of_agents_in_cluster)):
        for i in range(num_of_agents_in_cluster * j, j * num_of_agents_in_cluster + num_of_agents_in_cluster):
            random_num = random.randint(1,100)
            if random_num <= 10:#prob of having edge outside of cluster is 10%
                random_num = random.randint(0,total_population-1)
                while random_num in range(num_of_agents_in_cluster * j, j * num_of_agents_in_cluster + num_of_agents_in_cluster):
                    random_num = random.randint(0,total_population-1)
                    #wait
                if not (random_num in agents[i].neighbours):
                    agents[i].neighbours.append(random_num)
                    agents[random_num].neighbours.append(i)




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
        random_num = random.randint(1,100)
        if random_num == 2: #prob of having a superspreader in the cluster is 2%
            superspreaders.append(i)

    # print(superspreaders)
    for i in superspreaders:
            for j in range(total_population):
                random_num = random.randint(1,100)
                if(random_num<=60) and not (i in agents[j].neighbours):
                    agents[i].neighbours.append(j)
                    agents[j].neighbours.append(i)    


    return agents
    # for i in agents.keys():
    #     print(agents[i].id, agents[i].neighbours)