import datetime
import json
import os

import numpy as np
import pandas as pd

from qiskit import QuantumCircuit
from qiskit.algorithms.minimum_eigensolvers import QAOA
from qiskit.primitives import BackendSampler

from qiskit_optimization import QuadraticProgram
from qiskit_optimization.algorithms import MinimumEigenOptimizer


def input_tsp(filename):
    with open(filename) as f:
        firstline = next(f)
        data = []
        for lines in f:
            data.append(list(map(int, lines.split())))

    firstline = list(map(int, firstline.split()))
    v, e = firstline[0], firstline[1]

    cost_list = []

    for i in range(v):
        for j in range(v):
            cost_list.append(0)
            if i != j:
                for k in range(e):
                    if data[k][0] == i and data[k][1] == j:
                        cost_list[-1] = data[k][2]

    cost_list = np.array(cost_list).reshape(v, v)

    quad_mat = [[0 for i in range(v**2)] for j in range(v**2)]

    for i in range(v):
        for j in range(v):
            for k in range(v):
                if k != v - 1:
                    quad_mat[i * v + k][j * v + k + 1] = cost_list[i][j]
                else:
                    quad_mat[i * v + k][j * v] = cost_list[i][j]

    return quad_mat


def create_tsp(filename, n):
    tsp = QuadraticProgram("TSP")

    for i in range(n):
        for j in range(n):
            tsp.binary_var(name=f"x_{i}_{j}")

    tsp.minimize(quadratic=input_tsp(filename))

    for i in range(n):
        indice = [f"x_{i}_{j}" for j in range(n)]
        values = [1 for j in range(n)]
        dictionary = dict(zip(indice, values))
        tsp.linear_constraint(
            linear=dictionary,
            sense="==",
            rhs=1,
            name=f"c{i}",
        )

    for i in range(n):
        indice = [f"x_{j}_{i}" for j in range(n)]
        values = [1 for j in range(n)]
        dictionary = dict(zip(indice, values))
        tsp.linear_constraint(
            linear=dictionary,
            sense="==",
            rhs=1,
            name=f"c{i + n}",
        )

    return tsp


def w_cir(n):
    prob_amp = np.sqrt(1 / n)
    rot_ang = 2 * np.arccos(prob_amp)

    qc_w = QuantumCircuit(n)

    qc_w.x(0)

    for i in range(n - 1):
        comp_amp = np.sqrt(1 - i / n)
        rot_ang = 2 * np.arccos(prob_amp / (comp_amp))
        qc_w.cry(rot_ang, i, i + 1)
        qc_w.cx(i + 1, i)

    return qc_w


def create_init_state(n):
    qc = QuantumCircuit(n**2)
    qc.x(0)

    for i in range(1, n):
        qc.compose(
            w_cir(n - 1),
            qubits=[i * n + j for j in range(1, n)],
            inplace=True,
        )

    return qc


def execution(backend, options, optimizer, reps, qc=None):
    sampler = BackendSampler(backend=backend, options=options)

    if qc is None:
        qaoa = QAOA(
            sampler=sampler,
            optimizer=optimizer,
            reps=reps,
        )

    else:
        qaoa = QAOA(
            sampler=sampler,
            optimizer=optimizer,
            reps=reps,
            initial_state=qc,
        )

    meo = MinimumEigenOptimizer(min_eigen_solver=qaoa)

    return meo


def result_shower(result):
    if result.status.name == "SUCCESS":
        print(f"Result : {int(result.fval)}")

        variable_list = []
        for variable in result.variables_dict:
            if int(result.variables_dict[variable]) == 1:
                variable_list.append(variable)

        turn_table = [0 for i in range(len(variable_list))]
        for item in variable_list:
            turn_table[int(item[-1])] = int(item[-3])

        for i in range(len(turn_table)):
            if i != len(turn_table) - 1:
                print(f"City_{turn_table[i]}  →  ", end="")
            else:
                print(f"City_{turn_table[i]}  →  City_{turn_table[0]}")

    else:
        print("Result : FAILURE\n")

        for item in result.variables_dict:
            print(f"Variable [{item}] : {int(result.variables_dict[item])}")


def get_job_list():
    jobs_meta = '../config/job_conf.json'
    with open(jobs_meta) as f:
        jobs = json.load(f)

    job_dir = jobs['path'] + jobs['opt']
    jobs_filename = job_dir + '/jobs.csv'
    df = pd.read_csv(jobs_filename)

    job_created = []
    for i in range(len(df)):
        tmp_comp_time = str(df['Completed'][i])
        tmp_date, tmp_time = (
            tmp_comp_time.split('T')[0].split('-'),
            tmp_comp_time.split('T')[1].split('.')[0].split(':')
        )

        for j in range(3):
            tmp_date[j] = int(tmp_date[j])
            tmp_time[j] = int(tmp_time[j])

        tmp = datetime.datetime(
            tmp_date[0], tmp_date[1], tmp_date[2],
            tmp_time[0], tmp_time[1], tmp_time[2]
        )

        job_created.append([tmp, str(df['JobId'][i])])

    job_created = sorted(job_created)
    job_list = [job_created[i][1] for i in range(len(job_created))]

    return job_list, job_dir


def txt_to_json(job_dir, job_name, i):
    job = job_dir + '/' + job_name

    job_info = job + '-info.json'
    job_result = job + '-result.txt'

    renamed_job_info = job_info.replace(job_name, f'data_{i + 1}')
    os.rename(job_info, renamed_job_info)

    with open(job_result, 'r') as f:
        data = json.load(f)

    renamed_job_result = renamed_job_info.replace('info', 'result')
    with open(renamed_job_result, 'w') as f:
        json.dump(data, f, indent=4)

    os.remove(job_result)
