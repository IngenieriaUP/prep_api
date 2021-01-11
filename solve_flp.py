import time
import re
import numpy as np
import requests
from pulp import LpMinimize, LpProblem, LpVariable, lpSum, LpBinary

p = 3
c, f = 100, 50
candidates = [i for i in range(c)]
facilities = [f'FAC_{i}' for i in range(f)]
demand = {i: np.random.normal(20,6) for i in range(c)}
cost_dict = {facilities[i]: {candidates[j]: np.random.normal(1250,200) for j in range(c)} for i in range(f)}

#test api

response = requests.post('http://127.0.0.1:8000/optimize', json={
    'p': p,
    'candidates': candidates,
    'facilities': facilities,
    'cost': cost_dict,
    'demand': demand,
})

print(response.json())
