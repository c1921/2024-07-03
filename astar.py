import heapq
import numpy as np

def euclidean_heuristic(a, b):
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5

def astar(array, start, goal):
    neighbors = [(0, 1), (0, -1), (1, 0), (-1, 0), 
                 (1, 1), (-1, -1), (1, -1), (-1, 1)]
    
    close_set = set()
    came_from = {}
    gscore = {start: 0}
    fscore = {start: euclidean_heuristic(start, goal)}
    oheap = []
    heapq.heappush(oheap, (fscore[start], start))
    oheap_set = {start}
    
    while oheap:
        current = heapq.heappop(oheap)[1]
        oheap_set.remove(current)
        
        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            return path[::-1]
        
        close_set.add(current)
        
        for i, j in neighbors:
            neighbor = current[0] + i, current[1] + j
            tentative_g_score = gscore[current] + euclidean_heuristic(current, neighbor)
            
            if 0 <= neighbor[0] < array.shape[0]:
                if 0 <= neighbor[1] < array.shape[1]:
                    if array[int(neighbor[0])][int(neighbor[1])] == 1:  # 不可通行
                        continue
                else:
                    continue
            else:
                continue
                
            if neighbor in close_set and tentative_g_score >= gscore.get(neighbor, float('inf')):
                continue
                
            if tentative_g_score < gscore.get(neighbor, float('inf')) or neighbor not in oheap_set:
                came_from[neighbor] = current
                gscore[neighbor] = tentative_g_score
                fscore[neighbor] = tentative_g_score + euclidean_heuristic(neighbor, goal)
                if neighbor not in oheap_set:
                    heapq.heappush(oheap, (fscore[neighbor], neighbor))
                    oheap_set.add(neighbor)
                
    return []
