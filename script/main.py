import time
import json

from qiskit_algorithms.optimizers import COBYLA, NELDER_MEAD, POWELL, SPSA
from qiskit.providers import Options
from qiskit_ibm_runtime import QiskitRuntimeService
from qiskit_ibm_provider import IBMProvider

from utility_functions import (
    create_tsp,
    create_init_state,
    execution,
    result_shower
)


if __name__ == "__main__":
    with open('../config/meta.json') as f:
        meta_data = json.load(f)

    PROBLEM = create_tsp(
        meta_data['problem']['data_path'],
        meta_data['problem']['num_cities']
    )
    OPTION = Options(shots=meta_data['shots'])
    optimizer_dict = {
        "cobyla": COBYLA(maxiter=meta_data['iterations']),
        "nelder-mead": NELDER_MEAD(maxiter=meta_data['iterations']),
        "powell": POWELL(maxiter=meta_data['iterations']),
        "spsa": SPSA(maxiter=meta_data['iterations'])
    }
    OPTIMIZER = optimizer_dict[meta_data['optimizer']]
    REPS = meta_data['reps']

    QiskitRuntimeService.save_account(
        channel="ibm_quantum",
        token=meta_data['token'],
        overwrite=True
    )

    provider = IBMProvider()
    instance = "ibm-q/open/main"

    if meta_data['mode'] == 'simulation':
        backend_sim = provider.get_backend(
            "ibmq_qasm_simulator",
            instance=instance
        )

        meo_sim = execution(
            backend_sim,
            OPTION,
            OPTIMIZER,
            REPS,
            qc=create_init_state(meta_data['problem']['num_cities'])
        )

        start = time.time()
        result_sim = meo_sim.solve(PROBLEM)
        end = time.time()

        print(f"Time : {int(end - start)} sec")
        result_shower(result_sim)

    elif meta_data['mode'] == 'device':
        backend_device = provider.get_backend(
            meta_data['quantum_machine'],
            instance=instance
        )

        meo_device = execution(
            backend_device,
            OPTION,
            OPTIMIZER,
            REPS,
            qc=create_init_state(meta_data['problem']['num_cities'])
        )

        result_device = meo_device.solve(PROBLEM)

        result_shower(result_device)

    else:
        print('mode in meta data is incorrect')
