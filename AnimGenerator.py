import matplotlib.pyplot as plt
import matplotlib.animation as anim
import numpy as np

from DataHandler import *

class AnimGenerator:
    def __init__(self, pdata, g_type):
        global data, mosaic, vector_field, fig, graph_type
        graph_type = g_type
        data = pdata
        fig = plt.figure()

        if graph_type == 'm':
            mosaic = plt.imshow(data[0], animated=True)
        elif graph_type == 'vf':
            lim = np.linspace(0, len(data[0]), len(data[0]))
            u_data = data[0]
            v_data = data[1]
            vector_field = plt.quiver(lim, lim, u_data[0], v_data[0], alpha=.5, scale=1000, color=[0.3921, 0.4941, 0.6588], scale_units='inches')
        else:
            print('Error: Bad argument as graph type: {}'.format(g_type))

    def update(t):
        global data, mosaic, vector_field

        if graph_type == 'm':
            mosaic.set_array(data[t])
            return mosaic,
        elif graph_type == 'vf':
            vector_field.set_UVC(data[0][t], data[1][t])
            return vector_field,

    def show(self, export_flag, name="default_name.mp4"):
        global data, mosaic, fig, graph_type
        animation = None

        if graph_type == 'm':
            animation = anim.FuncAnimation(fig, AnimGenerator.update, frames=len(data), interval=100, blit=True, save_count = 1000)
        elif graph_type == 'vf':
            animation = anim.FuncAnimation(fig, AnimGenerator.update, frames=len(data[0]), interval=100, blit=False, save_count = 1000)
            # Es posible pasar argumentos: animation.FuncAnimation(fig, update_quiver, *fargs=(Q, X, Y), interval=50, blit=False)

        if export_flag == 1:
            plt.show()
        elif export_flag == 2:
            animation.save(name, fps=10, extra_args=['-vcodec', 'libx264'])

if __name__ == "__main__":
    dh = DataHandler()
    #dh.gen_example_data('testX.dat', 10, 10, 10)
    #dh.gen_example_data('testY.dat', 10, 10, 10)
    test_x = dh.load_data('u_timestamps.dat')
    test_y = dh.load_data('v_timestamps.dat')

    print(np.round(test_x[0]),3)
    print(np.round(test_y[0]),3)

    plt.quiver(np.linspace(0,10,10), np.linspace(0,10,10), test_x[0], test_y[1], alpha=.5)
    plt.show()
