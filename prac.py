import numpy as np
import tkinter as tk
import matplotlib
matplotlib.use('TkAgg')

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

root=tk.Tk()

fig=plt.figure(1)
t=np.arange(0.0, 3.0, 0.01)
s=np.sin(np.pi*t)
plt.plot(t, s)

canvas = FigureCanvasTkAgg(fig, master=root)
plot_widget=canvas.get_tk_widget()
plot_widget.grid(row=0, column=0)
root.mainloop()