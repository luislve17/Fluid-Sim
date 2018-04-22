import matplotlib.pyplot as plt
import matplotlib.animation as anim

class AnimGenerator:
    def __init__(self, pdata):
        global data, mosaic, fig
        data = pdata
        fig = plt.figure()
        # ax = plt.axes(xlim=xl, ylim=yl)
        # mosaic, = ax.plot([],[])
        mosaic = plt.imshow(data[0], animated=True)


    def update(t):
        global data, mosaic
        mosaic.set_array(data[t])
        return mosaic,

    def show(self, export_flag, name="default_video.mp4"):
        global data, mosaic, fig
        mosaic_animation = anim.FuncAnimation(fig, AnimGenerator.update, frames=len(data), interval=10, blit=True, save_count = 100)

        if export_flag == 1:
            plt.show()

        elif export_flag == 2:
            mosaic_animation.save(name, fps=60, extra_args=['-vcodec', 'libx264'])
