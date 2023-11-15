import numpy as np
from multiprocessing import Pool
from pendulums import count_flips, Constants


def fill_row(args):
    i, theta1, theta2s, cnst = args
    row = [count_flips(theta1, theta2, cnst) for theta2 in theta2s]
    return i, row


def get_resmap_multiproc(N: int, cnst: Constants, num_processes: int = 4) -> np.ndarray:
    theta1s = np.linspace(0, np.pi, N)
    theta2s = np.linspace(-np.pi, np.pi, 2*N-1)

    # Create a Pool of processes
    with Pool(num_processes) as pool:
        # Generate a list of arguments for each row
        row_args = [(i, theta1, theta2s, cnst) for i, theta1 in enumerate(theta1s)]

        # Use the pool to parallelize the execution of fill_row
        results = pool.map(fill_row, row_args)

    # Sort the results based on the original row indices
    results.sort()

    # Extract the filled rows from the results
    filled_rows = [row for _, row in results]

    # Create the resulting matrix
    res_map = np.array(filled_rows, dtype=int)

    return res_map


if __name__ == '__main__':
    ...
