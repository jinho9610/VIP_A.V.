from tkinter import *
from tkinter import ttk
import opti_test
import entire_map_plot
#import final_driving_pure
#import lane_detect_main

def callbackopti():
	global x1,y1
	b1=tk.Button(window,text='lane_maker')
	b1.place(x=0,y=20,width=100,height=100)
	final_driving_pure1.main(x1,y1)

def callbackmap():
	global x1,y1
	b3=Label(window,text='출발지')
	b3.pack()
	x1,y1=entire_map_plot.lookmap()
	print(x1," ",y1)
	b3["text"]="x : {}\ny : {}".format(x1,y1)

window=Tk()
window.title("MV CASTLE")
window.geometry("640x480+100+100")
window.resizable(False, False)

def close():
    window.quit()
    window.destroy()

bg=PhotoImage(file="mv_bg.gif")
img=Label(window, image=bg)
img.pack()

txtBox1=Label(window, text="How to Use?", font=(30))
txtBox2=Label(window, text="1. Set your destination", font=(30))
txtBox3=Label(window, text="2. Check your path", justify='center', font=(30))
txtBox1.place(x=30, y=150)
txtBox2.place(x=30, y=180)
txtBox3.place(x=30, y=210)

button1 = Button(window, relief="solid", text="TMP name", width=40, height=10, command=callbackopti)
button2 = Button(window, relief="solid", text="Setting Destination", width=40, height=10, command=callbackmap)
button1.pack(side="left", anchor='s', padx='13', pady='20')
button2.pack(side="right", anchor='s', padx='13', pady='20')
window.mainloop()

print("Window Close")