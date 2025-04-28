#######################################################STABLE MOUSE#######################################################
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  3 17:03:46 2023

@author: psyteam74
"""
import random
import numpy as np
from datetime import datetime

def findMiddle(input_list):
    middle = float(len(input_list))/2
    if middle % 2 != 0:
        return input_list[int(middle - .5)]
    else:
        return (input_list[int(middle)]) # if the list has a pair number of elements the returned value is the one after the middle one
     

going = True
dark = 0
nights = 0
stable_nights = []
percent_social_whole_night = []

class perf(): # master structure for some variables
    pass
p = perf() 

while going:
    now = datetime.now() 
    if now.hour < 8  or now.hour > 20:
        if dark == 0:
            dark = 1
            p.social = []
            p.retrieved = [] # the perfs are reset to 0 at the begining of the night
        
    elif now.hour > 8  and now.hour < 20:
        if dark == 1:
            dark = 0 # If there is a switch from dark to light...
            nights += 1
            
            
            #### optional part for real conditions ####
            p.social = []
            p.retrieved = []
            trial_per_night = random.randint(100, 2000)
            for i in range(0,trial_per_night): # Generate wieghted random social or non social choices and retrieved
                p.retrieved.append(int(np.random.choice([0,1], 1, p=[0.05, 0.95]))) # 95% of chance of retrived  
            for i in range(0, sum(p.retrieved)):
                #if i%40 == 0:
                p1 = 0.125 - random.random()/8
                p2 = 1-p1
                p.social.append(int(np.random.choice([0,1], 1, p=[p1, p2]))) # 70% of chance of social choice
            ################################################  
               
            
            ####### intra-session stability ###########
            # create "stop points" where the mice has retrieved 40 time in a row the reward (social or non social)
            temp_list = [] 
            success_stop_points_ret = []
            success_stop_points_soc = []
            for i in p.retrieved:
                temp_list.append(i) # checks the retrieved list in an iterative manner
                if sum(temp_list[-40:]) == 40: # all last 40 retrieved were equal to 1
                    last_point_soc = sum(temp_list) # We take th sum as index because we take only success retrieved (which has a corresponding social value)
                    last_point_ret = len(temp_list) # len of temp list to keep track of number of trials 
                    if len(success_stop_points_ret) >= 1:
                        if last_point_ret > success_stop_points_ret[-1]+40: # We check if this new stop point (last point), is at least superior by 40 to the last success stop point.
                            success_stop_points_soc.append(last_point_soc)
                            success_stop_points_ret.append(last_point_ret)
                    else:
                        success_stop_points_soc.append(last_point_soc)
                        success_stop_points_ret.append(last_point_ret)
            # check performance at beginning middle and end of the night
            if len(success_stop_points_soc) >= 3: # The mouse has to make at least three time 40 consecutive retrived (minimum 120 trial)
                percent_social = []
                for j in success_stop_points_soc:
                    percent_social.append(sum(p.social[j-40:j])/40)
                percent_social_comp = [percent_social[0], findMiddle(percent_social), percent_social[-1]]
                success_stop_points_comp = [success_stop_points_soc[0], findMiddle(success_stop_points_soc), success_stop_points_soc[-1]]
                # check if performance at beginning middle and end of the night are similar
                inside_tunnel_intra = []
                #mediane_percent_social  = np.median(percent_social_comp)
                for i in percent_social_comp[1:]:
                    if percent_social_comp[0] - 0.1 < i < percent_social_comp[0] + 0.1:
                        inside_tunnel_intra.append(1)
                    else:
                        inside_tunnel_intra.append(0)
                if inside_tunnel_intra == [1,1]: # check if social performance is constant at the three night timepoints
                    stable_nights.append(1)
                    percent_social_whole_night.append(sum(p.social)/len(p.social))
                    print("SUCCEED! Performance of the night: \n Purcent social choice: ",percent_social_comp)
                    p.social = []
                    p.retrieved = []
                else:
                    stable_nights.append(0)
                    print("FAILED! Performance of the night: \n Purcent social choice: ",percent_social_comp)
                    p.social = []
                    p.retrieved = []
                ####### inter-session stability ###########
                if len(stable_nights) >= 3:
                    if stable_nights[-3:] == [1,1,1]:
                        inside_tunnel_inter = [] 
                        for i in percent_social_whole_night[-2:]:
                            if percent_social_whole_night[-3] - 0.1 < i < percent_social_whole_night[-3] + 0.1:
                                inside_tunnel_inter.append(1)
                            else:
                                inside_tunnel_inter.append(0)
                        if  inside_tunnel_inter == [1,1]:# the first night (three nights ago) is the reference point (stable)
                            print("Mouse succeded the stage, end of experiment \n Performances whole nights ", percent_social_whole_night[-3:])
                            going = False
                        else:
                            print("NOT 3 CONSECUTIVE STABLE NIGHTS (",percent_social_whole_night[-3],"), START FROM 0: \n night stability:", percent_social_whole_night[-3:])
            else:
                print("FAILED: not enought success retrieved!")
                stable_nights.append(0)
                p.social = []
                p.retrieved = []