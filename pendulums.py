from dataclasses import dataclass

import numpy as np
from scipy.integrate import odeint

sin = np.sin
cos = np.cos
pi = np.pi


@dataclass
class Constants:
    g: float = 9.8
    l1: float = 1.
    l2: float = 1.
    m1: float = 1.
    m2: float = 1.
    T_final: int = 10

    def __iter__(self):
        # yield self.g; yield self.l1; yield self.l2; yield self.m1; yield self.m2; yield self.T_final
        yield from self.__dict__.values()


def right_hand_side(
        y: np.ndarray,
        t: float,
        cnst: Constants
    ) -> np.ndarray:
    th1, th2, om1, om2 = y
    g, l1, l2, m1, m2, _ = cnst
    dydt = [
        om1,
        om2,
        (-g*(2*m1+m2)*sin(th1)-m2*g*sin(th1-2*th2)-2*sin(th1-th2)*m2*(om2**2*l2+om1**2*l1*cos(th1-th2)))/(l1*(2*m1+m2-m2*cos(2*th1-2*th2))),
        (2*sin(th1-th2)*(om1**2*l1*(m1+m2)+g*(m1+m2)*cos(th1)+om2**2*l2*m2*cos(th1-th2)))/(l2*(2*m1+m2-m2*cos(2*th1-2*th2)))
    ]
    return np.array(dydt)


def to_xy_coords(th1: np.ndarray, th2: np.ndarray, cnst: Constants) -> tuple[np.ndarray, np.ndarray]:
    ball1 = [
        [cnst.l1*sin(theta1) for theta1 in th1],
        [-cnst.l1*cos(theta1) for theta1 in th1]
    ]
    ball2 = [
        [ball1[0][ind]+cnst.l2*sin(theta2) for ind,theta2 in enumerate(th2)],
        [ball1[1][ind]-cnst.l2*cos(theta2) for ind,theta2 in enumerate(th2)]
    ]
    return np.array(ball1), np.array(ball2)


def get_solution(init_theta1: float, init_theta2: float, cnst: Constants) -> tuple[np.ndarray, np.ndarray]:
    '''Get matrix with rows [theta1, theta2] for times [0, T]'''
    t = np.linspace(0., cnst.T_final, 201)
    y0 = np.array([init_theta1, init_theta2, 0., 0.])
    sol = odeint(right_hand_side, y0, t, args=(cnst, ))
    return t, sol


def get_flip_points(times: np.ndarray, theta2_angles: np.ndarray) -> np.ndarray:
    res = []
    for i, (t1, t2) in enumerate(zip(theta2_angles[:-1], theta2_angles[1:])):
        if int(t1 / np.pi) != int(t2 / np.pi) and int(t1 / np.pi) % 2 == 0:
            res.append(times[i])
    return res


def count_flips(init_theta1: float, init_theta2: float, cnst: Constants) -> int:
    t, sol = get_solution(init_theta1, init_theta2, cnst)
    return len(get_flip_points(t, sol.T[1]))


def get_resmap_sequential(N: int, cnst: Constants, verbose: bool = False) -> np.ndarray:
    res_map = np.zeros((N, 2*N-1), dtype=int)
    T_final = cnst.T_final
    if verbose:
        print(f'shape: {res_map.shape}; {np.prod(res_map.shape)} pixels; {T_final=}')

    theta1s = np.linspace(0, np.pi, N)
    theta2s = np.linspace(-np.pi, np.pi, 2*N-1)
    
    for i, t1 in enumerate(theta1s):
        for j, t2 in enumerate(theta2s):
            res_map[i, j] = count_flips(init_theta1=t1, init_theta2=t2, cnst=cnst)
        if verbose: print(f'.{i+1}.', end='')
    return res_map

