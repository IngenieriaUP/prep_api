import time
import re
import numpy as np
from pulp import LpMinimize, LpProblem, LpVariable, lpSum, LpBinary, LpStatus
from fastapi import FastAPI
from pydantic import BaseModel

class Model(BaseModel):
    p: int
    candidates: list
    facilities: list
    cost: dict
    demand: dict

def build_and_solve(p, candidates, facilities, cost, demand):

    start_build = time.time()
    prob = LpProblem('FLP_Markets_SJL', LpMinimize)
    x = LpVariable.dicts('Service',
                    [(i,j) for j in candidates for i in facilities],
                    0)
    y = LpVariable.dicts('Activation',
                     facilities,
                     0,1, LpBinary)

    prob += lpSum(lpSum(demand[str(j)]*cost[i][str(j)]*x[i,j] for i in facilities) for j in candidates)

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

    #prob.toJson('flp.json')

    x_vars = [[0 for i in range(len(candidates))] for j in range(len(facilities))]
    y_vars = [0 for i in range(len(facilities))]


    for v in prob.variables():
        if 'Activation' not in v.name:
            i, j = re.findall('\d+', v.name)
            x_vars[int(i)][int(j)] = int(v.varValue)

    for v in prob.variables():
        if 'Activation' in v.name:
            ix = int(re.findall('\d+', v.name)[0])
            y_vars[ix] = int(v.varValue)

    obj_value = prob.objective.value()
    status = LpStatus[prob.status]
    build_time = end_build-start_build
    solve_time = solve_end-solve_start

        ## TODO: add solver return and configurability?

    return build_time, solve_time, obj_value, x_vars, y_vars

app = FastAPI()

@app.post('/optimize/')
async def optimize(model: Model):
    build, solve, obj, assignments, facilities = build_and_solve(model.p, model.candidates,
                                                                   model.facilities, model.cost,
                                                                   model.demand)

    return {'build_time': build, 'solve_time': solve, 'obj_value': obj, 'assignments': assignments, 'facilities': facilities}
