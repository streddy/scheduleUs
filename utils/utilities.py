
from datetime import datetime, timedelta
import math
import numpy as np
#import cvxpy

## ----------------------------------------------------------------------------
## ----------------------- DATA FORMAT EXAMPLE --------------------------------
## ----------------------------------------------------------------------------
'''
poll_timeframe_start = datetime.strptime("2010-01-01 10:30:00", '%Y-%m-%d %H:%M:%S')

poll_timeframe_end = datetime.strptime("2010-01-01 23:10:00", '%Y-%m-%d %H:%M:%S')

event_length = [0.0, 50.0] # [#hrs, #minutes]

user_data_txt = [["2010-01-01 00:11:52","2010-01-01 23:13:00"],
                 ["2010-01-01 08:14:49","2010-01-01 15:21:00"],
                 ["2010-01-01 18:23:05","2010-01-01 19:29:00"],
                 ["2010-01-01 07:30:00","2010-01-01 21:30:36"],
                 ["2010-01-01 14:32:00","2010-01-01 23:33:00"],
                 ["2010-01-01 11:36:40","2010-01-01 22:36:55"],
                 ["2010-01-01 10:41:00","2010-01-01 17:48:17"],
                 ["2010-01-01 09:50:49","2010-01-01 22:51:00"],
                 ["2010-01-01 14:53:00","2010-01-01 21:56:00"],
                 ["2010-01-01 03:57:00","2010-01-01 18:57:35"],
                 ["2010-01-01 01:01:00","2010-01-01 23:04:37"],
                 ["2010-01-01 09:02:07","2010-01-01 13:08:32"],
                 ["2010-01-01 11:09:00","2010-01-01 16:16:00"],
                 ["2010-01-01 12:18:47","2010-01-01 20:21:00"],
                 ["2010-01-01 08:27:34","2010-01-01 13:29:07"],
                 ["2010-01-02 08:40:00","2010-01-04 13:30:07"],
                 ["2010-01-01 18:40:00","2010-01-03 07:30:07"],
                 ["2010-01-02 15:40:00","2010-01-05 16:30:07"]]

# each string is converted to datetime type but the overall format is the same 
# as user_data_txt
user_data_dt = [[datetime.strptime(date_time_str[0], '%Y-%m-%d %H:%M:%S'),
              datetime.strptime(date_time_str[1], '%Y-%m-%d %H:%M:%S')]
                                                     for date_time_str in user_data_txt]

options = [False,False]  # options[0]=True => meeting time can be flexible 
                         # options[1]=True => attendees can be late/leave early
'''
## ----------------------------------------------------------------------------
## --------------------------- FUNCTIONS -------------------------------------
## ----------------------------------------------------------------------------

def perdelta(start, end, delta):
    ''' 
    Generate times between start and end with time increment delta.
    
    Args:
        start (datetime): poll start time.
        end (datetime): poll end time.
        delta (timedelta): time increment.
    
    Returns:
        list: time_range (list of datetime)
        
    '''
    time_range = []
    curr = start
    time_range.append(curr)
    while curr < end:
        curr += delta
        time_range.append(curr)
    return time_range


def find_availabilities(event_length,start,end,user_data):
    '''
    Define time slots and generate availability matrix.
    
    Args:
        event_length (list): list of # hrs and # minutes that the event should 
            last -- e.g. [1.,20.] = 1hr 20min
        start (datetime): poll start time.
        end (datetime): poll end time.
        user_data (list of tuples): availabilities of users. Each tuple is 
            defined by a start datetime and an end datetime
    
    Returns:
        matrix of availabilities (np.array([n_users, n_steps])) with 1 if the 
            user is available during the corresponding time slot.
        number of time slots considered between poll start and end.
        list of datetime instances that decompose the poll horizon into shorter
            time slots
        time increment that defines the duration of a time slot
        
    '''
    # count number of overlaps for each time stamp between start_time and end_time
    time_increment = 10.  # min
    n_steps = int(math.ceil((event_length[0]*60+event_length[1])/time_increment))
    
    time_list = perdelta(start,end, timedelta(minutes=time_increment))
    availabilities = [([(user[0]<=time_list[idx]) and (user[1]>=time_list[idx+1]) for user in user_data]) 
                                                                        for idx in range(len(time_list)-1)]
    
    return np.transpose(np.array(availabilities).astype(int)), n_steps, time_list, time_increment


def create_problem_parameters(n_steps, availabilities, opts):
    '''
    Create constraints/objective function to solve the MILP.
    
    Args:
        n_steps (int): number of time slots considered between poll start and 
            end.
        availabilities (np.array): boolean matrix of availabilities of each user
            for each time slot.
        opts (bool): True if meeting attendees can arrive late/leave early,
            False otherwise.

    Returns:
        equality constraint matrix and RHS
        inequality constraint matrix and RHS
        decision variables' bounds
        objective function coefficients
        
    '''
    n_users,n_slots = availabilities.shape
    n_decisions = 2*n_slots
    
    # Objective function
    c = np.concatenate((np.zeros([n_slots,]),np.sum(availabilities,axis=0)))

    # Equality constraints
    U1 = np.concatenate((np.ones([1,n_slots]),np.zeros([1,n_slots])),axis=1)  # = 1
    U2 = np.concatenate((np.zeros([1,n_slots]),np.ones([1,n_slots])),axis=1)  # = n
    A_eq = np.concatenate((U1,U2),axis=0)
    b_eq = np.array([1,n_steps])
    
    # Inequality constraints
    if opts==0:  # attendees have to attend the whole meeting
        n_ub_constraints = 2*n_slots+2*n_users*n_slots
        A_ub = np.zeros([n_ub_constraints,2*n_slots])
        current_idx = 0
        for ii in range(n_slots):
            A_ub[ii,ii] = n_steps
            A_ub[ii,ii+n_slots:ii+n_slots+min(n_steps,n_slots-ii)] = -np.ones([1,min(n_steps,n_slots-ii)])
            current_idx += 1
        A_ub[current_idx,0] = -1
        A_ub[current_idx,n_slots] = 1
        current_idx += 1
        for ii in range(1,n_slots):
            A_ub[current_idx,ii] = -1
            A_ub[current_idx,ii+n_slots] = 1
            A_ub[current_idx,ii+n_slots-1] = -1
            current_idx += 1
        B = -A_ub[:n_slots,n_slots:]
        for jj in range(n_users):
            for ii in range(n_slots):
                A_ub[current_idx,ii] = n_steps*availabilities[jj,ii]
                current_idx += 1
        for jj in range(n_users):
            for ii in range(n_slots):
                A_ub[current_idx,ii] = B.dot(availabilities[jj])[ii]
                current_idx += 1

        b_ub = np.concatenate((np.zeros([2*n_slots,]),np.concatenate([B.dot(item) for item in availabilities]),
                                                                               n_steps*availabilities.flatten()))

    elif opts==1:  # attendees can be 10min late/leave 10min early
        n_ub_constraints = 2*n_slots
        A_ub = np.zeros([n_ub_constraints,2*n_slots])
        current_idx = 0
        for ii in range(n_slots):
            A_ub[ii,ii] = n_steps
            A_ub[ii,ii+n_slots:ii+n_slots+min(n_steps,n_slots-ii)] = -np.ones([1,min(n_steps,n_slots-ii)])
            current_idx += 1
        A_ub[current_idx,0] = -1
        A_ub[current_idx,n_slots] = 1
        current_idx += 1
        for ii in range(1,n_slots):
            A_ub[current_idx,ii] = -1
            A_ub[current_idx,ii+n_slots] = 1
            A_ub[current_idx,ii+n_slots-1] = -1
            current_idx += 1
        B = -A_ub[:n_slots,n_slots:]

        b_ub = np.zeros([2*n_slots,])
        
    else:
        raise ValueError('Wrong options value')
    
    # Boundaries
    bounds = ()
    for kk in range(n_decisions):
        bounds = bounds + ((0,1),)
    
    return A_eq, b_eq, A_ub, b_ub, bounds, c


def solve_problem(A_eq, b_eq, A_ub, b_ub, c, n_steps, opts, data = None):
    '''
    Solve MILP problem defined by:
        max c*x/n
        s.t. A_eq*x = b_eq
             A_ub*x ≤ b_ub
             0≤x≤1
    If no solution, output will be (None, None)

    Args:
        A_eq, b_eq (np.array): equality constraint matrix and RHS
        A_ub, b_ub (np.array): inequality constraint matrix and RHS
        c (np.array): objective function coefficients
        n_steps (int): number of time slots considered between poll start and 
            end.
        opts (bool): True if meeting attendees can arrive late/leave early,
            False otherwise.
        data (optional): boolean matrix of availabilities of each user for each 
            time slot.
    
    Returns:
        int: optimal objective function value or None
        np.array: optimal solution or None
            
    '''
    z_len = int(len(c)/2)
    best_obj, best_sol = None, None
    
    time_shift = 2  # => max delay / earliness = 2*time_increment [min]
    
    if opts==0:
#        print('Attendees cannot be late')
        for pp in range(z_len):
            z, x = np.zeros([z_len,]), np.zeros([z_len,])
            z[pp] = 1
            x[pp:pp+min(n_steps,z_len-pp)] = 1
            sol = np.concatenate((z,x))
    
            if sum(A_eq.dot(sol)==b_eq) == 2 and sum(A_ub.dot(sol)<=b_ub) == A_ub.shape[0]:
                obj = c.dot(sol)
                if not best_obj or best_obj<obj:
                    best_obj = obj
                    best_sol = sol
        if best_obj:
            return best_obj/float(n_steps), best_sol
        else:
            return best_obj, best_sol
    
    elif opts==1:
#        print('Attendees can be late')
        for pp in range(z_len):
            z, x = np.zeros([z_len,]), np.zeros([z_len,])
            z[pp] = 1
            x[pp:pp+min(n_steps,z_len-pp)] = 1
            sol = np.concatenate((z,x))
            if sum(A_eq.dot(sol) == b_eq) == 2 and sum(A_ub.dot(sol) <= b_ub) == A_ub.shape[0] and len([item for item in x.dot(np.transpose(data)) if item in range(1,n_steps-time_shift)])==0:
                obj = c.dot(sol)
                if not best_obj or best_obj<obj:
                    best_obj = obj
                    best_sol = sol
        if best_obj:
            return best_obj/float(n_steps), best_sol
        else:
            return best_obj, best_sol
        

def run_algorithm(event_length,poll_timeframe_start,poll_timeframe_end,user_data_dt,options):
    '''
    Solve MILP problem with the following options:
        - option 1: solve the problem for the exact meeting time
        - option 2: try to reduce meeting time to increase attendance (by at most 20min)
        - option 3: allow for attendees to be slightly late/to leave slightly early
    If no meeting is possible given the options, it will automatically reduce the meeting
    duration to find a possible meeting time.
    
    Args:
        event_length (list): list of # hrs and # minutes that the event should 
            last -- e.g. [1.,20.] = 1hr 20min
        poll_timeframe_start (datetime): poll start time.
        poll_timeframe_end (datetime): poll end time.
        user_data_dt (list of tuples): availabilities of users. Each tuple is 
            defined by a start datetime and an end datetime
        options (list of bool): 0: True if fixed meeting time, False otherwise, 
            1: True if attendees can arrive late/leave early.

    Returns:
        datetime.day: meeting start day
        datetime.time: meeting start time
        int: meeting duration in minutes
        
    '''
    a_ji,n, time_list, time_increment = find_availabilities(event_length,poll_timeframe_start,poll_timeframe_end,user_data_dt)
    if options[1]==1:  # attendees can be late/leave early
        av = a_ji
    else:  # attendees cannot...
        av = None
    
    meeting_time_decrease = int(20./time_increment) + 1  # => max reduction: 20min
    
    if options[0]==0:  # meeting time is set
#        print('Meeting time fixed')
        A_eq, b_eq, A_ub, b_ub, bounds, c = create_problem_parameters(n, a_ji, options[1])
        opt_sol = solve_problem(A_eq, b_eq, A_ub, b_ub, c, n, options[1], data=av)
        opt_n = n
    elif options[0]==1:  # meeting time is flexible
#        print('Meeting time flexible')
        opt_sol = (None, None)
        opt_n = None
        for ss in range(n,max(n-meeting_time_decrease,0),-1):
            A_eq, b_eq, A_ub, b_ub, bounds, c = create_problem_parameters(ss, a_ji, options[1])
            sol_ss = solve_problem(A_eq, b_eq, A_ub, b_ub, c, ss, options[1], data=av)
#            print('meeting time [min]: ', ss*time_increment, '     ' , sol_ss[0])
            if sol_ss and (not opt_sol[0] or sol_ss[0]>opt_sol[0]):
                opt_sol, opt_n = sol_ss, ss
    else:
        raise ValueError('Wrong options value')

    if opt_sol[0]:
        meeting_day = time_list[np.where(opt_sol[1][:int(len(opt_sol[1])/2)])[0][0]].date()
        meeting_time = time_list[np.where(opt_sol[1][:int(len(opt_sol[1])/2)])[0][0]].time()
        meeting_duration = opt_n*time_increment
#        print('Meeting should start on ' + str(meeting_day) + ' at ' + str(meeting_time))
#        print('Meeting should last ' + str(meeting_duration) + ' minutes')
        
        return meeting_day, meeting_time, meeting_duration
                
    else:
#        print('No feasible meeting for the options selected')
        ss=n-1
        while (not opt_sol[0]) and ss>2:
            A_eq, b_eq, A_ub, b_ub, bounds, c = create_problem_parameters(ss, a_ji, options[1])
            opt_sol = solve_problem(A_eq, b_eq, A_ub, b_ub, c, ss, options[1])            
            ss -= 1
        if opt_sol[0]:
            meeting_day = time_list[np.where(opt_sol[1][:int(len(opt_sol[1])/2)])[0][0]].date()
            meeting_time = time_list[np.where(opt_sol[1][:int(len(opt_sol[1])/2)])[0][0]].time()
            meeting_duration = ss*time_increment
#            print('Suggested meeting time: ' + str(meeting_duration) + ' minutes')
#            print('Suggested meeting should start on ' + str(meeting_day) + ' at ' + str(meeting_time))

#            return opt_sol, time_list, ss, a_ji, A_ub
            return meeting_day, meeting_time, meeting_duration
        else:
            return None, None, None



## Solve using cvxpy
#selection = cvxpy.Bool(len(sol[1]))  # The variable we are solving for
#inequality_constraint = A_ub * selection <= b_ub
#equality_constraint = A_eq * selection == b_eq
#total_utility = c * selection  # total utility is the sum of the item utilities
#
## We tell cvxpy that we want to maximize total utility subject to weight_constraint.
## All constraints in cvxpy must be passed as a list
#scheduling_problem = cvxpy.Problem(cvxpy.Maximize(total_utility), [inequality_constraint, equality_constraint])
#
#start_time_2 = time.time()
#scheduling_problem.solve(solver=cvxpy.GLPK_MI)  # Solving the problem
#
#print(time.time()-start_time_2)
#print(selection.value)
#temp = selection.value
#print('Meeting should start at ', time_list[np.where(temp[:int(len(temp)/2)])[0][0]])
#print('Number of people attending :',scheduling_problem.value/float(n))
