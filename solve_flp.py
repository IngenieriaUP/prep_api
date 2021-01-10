import time
import re
import numpy as np
from pulp import LpMinimize, LpProblem, LpVariable, lpSum, LpBinary

p = 3
c, f = 100, 50
candidates = [i for i in range(c)]
facilities = [f'FAC_{i}' for i in range(f)]
demand = {i: np.random.normal(20,6) for i in range(c)}
cost_dict = {facilities[i]: {candidates[j]: np.random.normal(1250,200) for j in range(c)} for i in range(f)}

def build_and_solve(p, candidates, facilities, cost, demand):
    start_build = time.time()
    prob = LpProblem('FLP_Markets_SJL', LpMinimize)
    x = LpVariable.dicts('Service',
                    [(i,j) for j in candidates for i in facilities],
                    0)
    y = LpVariable.dicts('Activation',
                     facilities,
                     0,1, LpBinary)


    prob += lpSum(lpSum(demand[j]*cost_dict[i][j]*x[i,j] for i in facilities) for j in candidates)

    for j in candidates:
        prob += lpSum(x[i,j] for i in facilities) == 1

    prob += lpSum(y[i] for i in facilities) == p

    for i in facilities:
        for j in candidates:
            prob += x[i,j] <= y[i]

    end_build = time.time()

    solve_start = time.time()
    prob.solve()
    solve_end = time.time()

    prob.toJson('flp.json')

    # x_vars = np.zeros_like((len(candidates), len(facilities)))
    # y_vars = np.zeros_like(len(facilities))
    #
    # for v in prob.variables():
    #     if 'Activation' not in v.name:
    #         i, j = re.findall('\d+', v.name)
    #         x_vars[int(i),int(j)] = v.varValue
    #
    # for v in prob.variables():
    #     if 'Activation' in v.name:
    #         ix = int(re.findall('\d+', v.name)[0])
    #         y_vars[ix] = v.varValue
    #
    # x_vars, y_vars = x_vars.astype(int), y_vars.astype(int)
    #
    # np.save('demand_assignment.npy', x_vars)
    # np.save('facilities.npy', y_vars)

# build_and_solve(p, candidates, facilities, cost_dict, demand)

import requests

#test api

#build_and_solve(p, candidates, facilities, cost_dict, demand)

response = requests.post('http://127.0.0.1:8000/optimize', json={
    'p': p,
    'candidates': candidates,
    'facilities': facilities,
    'cost': cost_dict,
    'demand': demand,
})

print(response.json())
