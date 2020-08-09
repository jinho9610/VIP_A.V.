#-*- coding:utf-8 -*-
import glob
import matplotlib.pyplot as plt
import statistics
import glob
from tkinter import *
import opti_test
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

def lookmap():
	window=Tk()
	window.title("YU GWANG SOO")
	window.geometry("640x480+100+100")
	window.resizable(False, False)

	def close():
	    window.quit()
	    window.destroy()
	def add_point(event):
    	
	    if event.button == 1:
	        x = event.xdata
	        y = event.ydata
	        global x1,y1
	       	x1,y1=x,y
	 
	    if event.button == 3:
	        plt.disconnect(cid)

	files = glob.glob('*.txt') 
	x_points = []
	y_points = []
	fig = plt.figure()
	# plt.axis([-100, 300, 100, 550])
	plt.grid(True)
	plt.tight_layout()

	for file in files:
		f = open(file,'r')

		if len(file) == 8:
			temp_name = file[0:4]
		elif len(file) ==9:
			temp_name = file[0:4]
		else:
			pass

		globals()['Lane{}'.format(temp_name)]  = str(temp_name)

		while True:
			line = f.readline()
			if not line:
				break

			x_points.append(float(line.split()[0]))
			y_points.append(float(line.split()[1]))


		x_text_pos = x_points[int(len(x_points)/2)]
		y_text_pos = y_points[int(len(y_points)/2)]
		f.close()

		plt.plot(x_points, y_points)
		plt.scatter(x_points, y_points, marker='.')
		plt.text(x_text_pos, y_text_pos, globals()['Lane{}'.format(temp_name)])

		
		x_points = []
		y_points = []

	cid = plt.connect('button_press_event', add_point)

	canvas = FigureCanvasTkAgg(fig, master=window)
	plot_widget=canvas.get_tk_widget()
	plot_widget.grid(row=0, column=0)

	window.mainloop()

	return x1,y1

def callbackopti():
	b1=Button(window,text='lane_maker')
	b1.place(x=0,y=20,width=100,height=100)
	opti_test.make_txt()
def callbackmap():
	global x1,y1
	b3=Label(window,text='출발지')
	b3.pack()
	x1,y1=entire_map_plot.lookmap()
	print(x1," ",y1)
	b3["text"]="x : {}\ny : {}".format(x1,y1)


if __name__ == '__main__':
	lookmap()
	print(x1)