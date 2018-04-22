from AnimGenerator import *
from DataHandler import *

import numpy as np
import math

class Fluid:
    def __init__(self, grid_rows, grid_cols, diff_c, visc_c):
        self.N_rows = grid_rows
        self.N_cols = grid_cols

        self.D = np.zeros((grid_rows+2, grid_cols+2))
        self.D_0 = np.zeros((grid_rows+2, grid_cols+2))

        self.U = np.zeros((grid_rows+2, grid_cols+2))
        self.U_0 = np.zeros((grid_rows+2, grid_cols+2))

        self.V = np.zeros((grid_rows+2, grid_cols+2))
        self.V_0 = np.zeros((grid_rows+2, grid_cols+2))

        self.diff_coef = diff_c
        self.visc_coef = visc_c

        self.d_file = None

    '''
    - set_boundry(self, mode)
        * mode: Sets boundry condition to up-down wall (1) or left-right (2)
    '''
    def set_boundry(self, matrix, mode):
        # Cleaning up indexing
        nr = self.N_rows
        nc = self.N_cols

        for i in range(1,nr+1):
            for j in range(1,nc+1):
                matrix[0,i] = -matrix[1,i] if mode==1 else matrix[1,i]
                matrix[nr+1,i] = -matrix[nr,i] if mode==1 else matrix[nr,i]
                matrix[i,0] = -matrix[i,1] if mode==2 else matrix[i,1]
                matrix[i,nc+1] = -matrix[i,nc] if mode==2 else matrix[i,nc]

        # Setting corner values
        matrix[0,0] = 0.5*(matrix[0,1]+matrix[1,0])
        matrix[0,nc+1] = 0.5*(matrix[1,nc+1]+matrix[0,nc])
        matrix[nr+1,0] = 0.5*(matrix[nr,0]+matrix[nr+1,1])
        matrix[nr+1,nc+1] = 0.5*(matrix[nr,nc+1]+matrix[nr+1,nc])

    '''
    - def add_source(self, dt, factor)
        * dt: Iterator
        * matrix: To update matrix
        * source: Values used to update matrix
        * factor: Debug factor of release for the sources
    '''
    def add_source(self, matrix, source, dt):
        matrix += source*dt


    '''
    - def diffuse(self, matrix, matrix_0, mode, dt)
        * matrix: Matrix to update
        * matrix_0: Matrix with last time's values
        * mode: Set boundry mode
        * coef: Diffusion/Viscosity coeficient
        * dt: Iterator
    '''
    def diffuse(self, matrix, matrix_0, coef, mode, dt):
        a = dt*coef*self.N_rows*self.N_cols
        nr = self.N_rows
        nc = self.N_cols

        for iter in range(0,20):
            #print(matrix)
            #print(iter)
            for i in range(1, nr+1):
                for j in range(1, nc+1):
                    matrix[i,j] = matrix_0[i,j] + a*(matrix[i-1,j] + matrix[i+1,j] + matrix[i,j+1] + matrix[i,j-1])/(1 + 4*a)
            self.set_boundry(matrix, mode)


    '''
    - def advect(self, matrix, matrix_0, mode, dt)
        * matrix: Matrix to update
        * matrix_0: Matrix with last time's values
        * mode: Set boundry mode
        * dt: Iterator
    '''
    def advect(self, matrix, matrix_0, u_mat, v_mat, mode, dt):
        dt0 = dt*self.N_rows

        for i in range(1,self.N_rows+1):
            for j in range(1, self.N_cols+1):
                x = i - dt0*u_mat[i,j]
                y = j - dt0*v_mat[i,j]

                if x < 0.5:
                    x = 0.5
                if x > self.N_cols + 0.5:
                    x = self.N_cols + 0.5
                if y < 0.5:
                    y = 0.5
                if y > self.N_rows + 0.5:
                    y = self.N_rows + 0.5

                i0 = int(x)
                j0 = int(y)
                i1 = i0 + 1
                j1 = j0 + 1

                s1 = x - i0
                s0 = 1 - s1
                t1 = y - j0
                t0 = 1 - t1

                matrix[i,j] = s0*(t0*matrix_0[i0,j0] + t1*matrix_0[i0,j1]) + s1*(t0*matrix_0[i1,j0] + t1*matrix_0[i1,j1]);

        self.set_boundry(matrix, mode);

    def density_step(self, dt):
        self.add_source(self.D, self.D_0, dt)
        self.D, self.D_0 = self.D_0, self.D#Fluid.swap_mats(self.D, self.D_0)
        self.diffuse(self.D, self.D_0, self.diff_coef, 0, dt)
        self.D, self.D_0 = self.D_0, self.D#Fluid.swap_mats(self.D, self.D_0)
        self.advect(self.D, self.D_0, self.U, self.V, 0, dt)

    def velocity_step(self, dt):
        self.add_source(self.U, self.U_0, dt)
        self.add_source(self.V, self.V_0, dt)

        self.U_0, self.U = self.U, self.U_0#Fluid.swap_mats(self.U_0, self.U)

        self.diffuse(self.U, self.U_0, self.visc_coef, 1, dt)
#        print(f.V_0)
#        print(f.V)
        self.V_0, self.V = self.V, self.V_0#Fluid.swap_mats(self.V_0, self.V)
        self.diffuse(self.V, self.V_0, self.visc_coef, 2, dt)

        self.project_vel()
#        print(f.U_0)
#        print(f.U)
#        print(f.V_0)
#        print(f.V)
#        quit()

        self.U_0, self.U = self.U, self.U_0#Fluid.swap_mats(self.U_0, self.U)
        self.V_0, self.V = self.V, self.V_0#Fluid.swap_mats(self.V_0, self.V)
        self.advect(self.U, self.U_0, self.U_0, self.V_0, 1, dt)
        #print(f.U_0)
        #print(f.U)
        #quit()
        self.advect(self.V, self.V_0, self.U_0, self.V_0, 2, dt)
        self.project_vel();

    def project_vel(self):
        h = 1.0/self.N_rows
        nr = self.N_rows
        nc = self.N_cols

        for i in range(1, nr+1):
            for j in range(1, nc+1):
                self.V_0[i,j] = -0.5*h*(self.U[i+1,j] - self.U[i-1,j] + self.V[i,j+1] - self.V[i,j-1])
                self.U_0[i,j] = 0

        self.set_boundry(self.V_0, 0)
        self.set_boundry(self.U_0, 0)

        for iter in range(0,20):

            #print(iter)
            for i in range(1,nr+1):
                for j in range(1, nc+1):
                    self.U_0[i,j] = (self.U_0[i,j] + self.U_0[i-1,j] + self.U_0[i+1,j] + self.U_0[i,j-1] + self.U_0[i,j+1])/4

            self.set_boundry(self.U_0, 0)

        #print(self.V)
        for i in range(1, nr+1):
            for j in range(1,nc+1):
                self.U[i,j] -= 0.5*(self.U_0[i+1,j] - self.U_0[i-1,j])/h
                self.V[i,j] -= 0.5*(self.U_0[i,j+1] - self.U_0[i,j-1])/h

        #print(self.V)
        self.set_boundry(self.U, 1)
        self.set_boundry(self.V, 2)
        #print(self.V)

    @staticmethod
    def swap_mats(m1, m2):
        return m2, m1


    '''
    -----------------------------------
    Data handler and animation methods
    -----------------------------------
    This methods are not involved in the calculus process and are only tools
    for storing the data and visualizing the simulation
    '''

    def prepare_density_data(self, num_timestamps):
        self.d_file = open("density_timestamps.dat", "w")

        self.d_file.write("{} {} {}\n".format(self.N_rows+2, self.N_cols+2, num_timestamps))
        self.d_file.write("=====\n")

        self.d_file.close()

    def add_density_data(self):
        n_row = self.N_rows+2
        n_col = self.N_cols+2

        self.d_file = open("density_timestamps.dat", "a")

        for i in range(0, n_row):
            for j in range(0, n_col):
                self.d_file.write("{} ".format(self.D[i,j]))
            self.d_file.write("\n")
        self.d_file.write("=====\n")

        self.d_file.close()


def process(f, dt):
    f.U_0[0,int(f.N_cols/2)] = -0.1;
    f.V_0[0,int(f.N_cols/2)] = 0.4;
    f.U_0[0,int(f.N_cols/2)-1] = -0.1;
    f.V_0[0,int(f.N_cols/2)-1] = 0.4;
    f.U_0[0,int(f.N_cols/2)+1] = -0.1;
    f.V_0[0,int(f.N_cols/2)+1] = 0.4;

    f.U_0[int(f.N_rows/2),0] = 0.5;
    f.V_0[int(f.N_rows/2),0] = 0.2;
    f.U_0[int(f.N_rows/2)-1,0] = 0.5;
    f.V_0[int(f.N_rows/2)-1,0] = 0.2;
    f.U_0[int(f.N_rows/2)+1,0] = 0.5;
    f.V_0[int(f.N_rows/2)+1,0] = 0.2;

    f.D[4,int(f.N_cols/2)] = 0.1;
    f.D[int(f.N_rows/2),4] = 0.09;
    f.D[int(f.N_rows/2),int(f.N_cols/2)] = 0.11;

    f.velocity_step(dt)
    f.density_step(dt)

def init(f):
    f.D_0[int(f.N_rows/5), int(f.N_cols/5)] = 0.1

if __name__ == "__main__":
    f = Fluid(100,100, .02, 0.1)
    steps = 100;
    dt = 0.001;

    init(f)

    f.prepare_density_data(steps)

    for i in range(1, steps):
        process(f, dt)
        print("{}%".format(100*i/steps))
        f.add_density_data()

    dh = DataHandler()
    density_data = dh.load_data("density_timestamps.dat")

    anim = AnimGenerator(density_data)
    anim.show(2, "fluid_sim.mp4")
