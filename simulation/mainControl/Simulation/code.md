
## 1.仿真过程中无人机指令相关数据格式：
	
        uav_static_param --无人机静态参数数据格式
            {uav_id: [uav_id, uav_type_category, uav_type_id, action_interval_time, radius]}
        
        uav_speed -- 无人机飞行速度数据格式
            {uav_id: uav_speed}
        
        uav_load -- 无人机当前载弹量数据格式
            {uav_id: uav_load}
            
        uav_max_distance -- 无人机当前载弹量数据格式
            {uav_id: max_distance}
            
        uav_distance --无人机当前飞行距离数据格式
            {uav_id: distance}
    
        gazebo_uav_status --无人机真实数据返回指令格式：
            [[uav_id, uav_real_position, uav_orientation, uav_action_status, uav_next_point, action_keep_time]]
            
        shared_current_uav_status --仿真中需要保存至数据库的实时状态数据格式：
            [[uav_id, str(uav_real_position), str(uav_orientation), 
                uav_name, uav_type_id, experiment_id, current_step, uav_current_load, current_max_distance,
                    current_map_x, current_map_y, current_map_z, Q_x, Q_Y, Q_z, Q_w]]
                    
        pre_step_uav_status和current_all_uav_status --重规划时需要用到的无人机当前态势数据格式：
            [[uav_id, uav_real_position, uav_orientation, uav_action_status, uav_next_point, action_keep_time, 
                uav_name, uav_type_id, experiment_id, current_step, uav_current_load, current_max_distance]]

## 2. 飞行预测仿真
#### 函数名： get_next_second_uav_status()
#### 参数： 
        order_type_dict, uav_speed_dict, uav_position_dict, route_point_number_dict,
        task_finished_time_dict, step, map_list, route, single_task, action_interval_time_dict

#### 输入示例：
        order_type_dict:{1184:2}, 
        uav_speed_dict: {1184: 17.0}, 
        uav_position_dict: {1184: [650,650,500]}, 
        route_point_number_dict:{1184: 10}, 
        task_finished_time_dict: {1184: 2}, 
        step: 1000, 
        map_list: TODO, 
        route_list: TODO, 
        single_task_list: {1184: [1]}, 
        action_interval_time_dict: {1184: 10000}
#### 输出示例：
        如[[1,[0,0,0], 2], [2, [1,1,1], 1]]表示uav_id为1的无人机当前在[0,0,0]的位置，
        当前状态为2，为侦察状态；uav_id为2的无人机当前在[1,1,1]的位置，当前状态为1，为飞行状态

## 3. task相关数据格式
        all_task_id: {1184:[0,1]}
        all_task_position: {1184: ['16,15,92', '1,1,96']}
        all_task_profit: {0:6, 1:0}
        all_task_start_flag: {1184: [False, False]}
        all_task_work_time: {1184: [1, 0]}
        all_uav_id: [1184]