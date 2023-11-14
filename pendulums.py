import numpy as np
from scipy.integrate import odeint

sin = np.sin
cos = np.cos
pi = np.pi
g = 9.8
l1 = 1.
l2 = 1.
m1 = 1.
m2 = 1.

def right_hand_side(
        y: np.ndarray,
        t: float,
        g: float,
        l1: float, l2: float,
        m1: float, m2: float
    ) -> np.ndarray:
    th1, th2, om1, om2 = y
    dydt = [
        om1,
        om2,
        (-g*(2*m1+m2)*sin(th1)-m2*g*sin(th1-2*th2)-2*sin(th1-th2)*m2*(om2**2*l2+om1**2*l1*cos(th1-th2)))/(l1*(2*m1+m2-m2*cos(2*th1-2*th2))),
        (2*sin(th1-th2)*(om1**2*l1*(m1+m2)+g*(m1+m2)*cos(th1)+om2**2*l2*m2*cos(th1-th2)))/(l2*(2*m1+m2-m2*cos(2*th1-2*th2)))
    ]
    return np.array(dydt)

def to_xy_coords(th1: np.ndarray, th2: np.ndarray, l1: float, l2: float) -> tuple[np.ndarray, np.ndarray]:
    ball1 = [
        [l1*sin(theta1) for theta1 in th1],
        [-l1*cos(theta1) for theta1 in th1]
    ]
    ball2 = [
        [ball1[0][ind]+l2*sin(theta2) for ind,theta2 in enumerate(th2)],
        [ball1[1][ind]-l2*cos(theta2) for ind,theta2 in enumerate(th2)]
    ]
    return np.array(ball1), np.array(ball2)

def get_solution(T_final: float, init_theta1: float, init_theta2: float) -> tuple[np.ndarray, np.ndarray]:
    '''Get matrix with rows [theta1, theta2] for times [0, T]'''
    t = np.linspace(0., T_final, 201)
    y0 = np.array([init_theta1, init_theta2, 0., 0.])
    sol = odeint(right_hand_side, y0, t, args=(g,l1,l2,m1,m2))
    return t, sol

def get_flip_points(times: np.ndarray, theta2_angles: np.ndarray) -> np.ndarray:
    res = []
    for i, (t1, t2) in enumerate(zip(theta2_angles[:-1], theta2_angles[1:])):
        if int(t1 / np.pi) != int(t2 / np.pi) and int(t1 / np.pi) % 2 == 0:
            res.append(times[i])
    return res

def count_flips(T_final: float, init_theta1: float, init_theta2: float) -> int:
    t, sol = get_solution(T_final, init_theta1, init_theta2)
    return len(get_flip_points(t, sol.T[1]))

