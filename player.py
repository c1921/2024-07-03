import numpy as np
from config import real_time_per_game_hour

def move_player_towards_target(player_pos, target_pos, elapsed_time, move_speed, path):
    """
    移动玩家角色朝向目标位置，每小时移动move_speed个地块的距离。
    
    参数:
    player_pos: list, 玩家角色的当前坐标 [x, y]
    target_pos: list, 玩家角色的目标坐标 [x, y]
    elapsed_time: float, 自上次更新以来的时间，以秒为单位
    move_speed: float, 玩家每小时移动的地块数
    path: list, 路径点列表
    
    返回:
    player_pos: list, 更新后的玩家角色坐标
    target_pos: list, 如果已到达目标位置，则为 None
    path: list, 更新后的路径
    reached: bool, 是否到达目标位置
    """
    reached = False
    if path:
        next_step = path[0]
        dx = next_step[0] - player_pos[0]
        dy = next_step[1] - player_pos[1]
        distance = (dx ** 2 + dy ** 2) ** 0.5
        move_distance = move_speed * (elapsed_time / real_time_per_game_hour)
        
        if distance <= move_distance:
            player_pos = list(next_step)
            path.pop(0)
            if not path:
                target_pos = None
                reached = True
        else:
            angle = np.arctan2(dy, dx)
            player_pos[0] += move_distance * np.cos(angle)
            player_pos[1] += move_distance * np.sin(angle)
    return player_pos, target_pos, path, reached
