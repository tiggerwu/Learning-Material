from tkinter import *
import random
import tkinter.messagebox as tkMessageBox
from PIL import Image, ImageTk 
import sys,os
path = os.path.abspath(os.path.dirname(sys.argv[0]))
from generate import main

def Display():
    root = Tk()
    root.title('Posts Generation')
    Label(root,text = 'Posts Generation',font=('Arial', 17)).grid(row=1,sticky=None)
    Label(root,text = '          ',font=('Arial', 17)).grid(row=3,sticky=None)
    Label(root,text = '###Please choose the mode###',font=('Arial', 15)).grid(row=3,sticky=None)

    image = Image.open(path + '/background.jpg') 
    img = ImageTk.PhotoImage(image)
    canvas = Canvas(root, width = image.width ,height = image.height, bg = 'white')
    canvas.create_image(0,0,image = img,anchor="nw")
    canvas.grid()   

    Label(root,text = '               ',font=('Arial', 15)).grid(row=19,sticky=None)
    Button(root, text = "Generate",width=8,height=2,command = Display1,font=('Arial', 15))\
           .grid(row = 20, column=0,sticky=W)
    Label(root,text = '---used to generate \n posts from three \n platforms',font=('Arial', 10)).grid(row=21,column=0,sticky=W)
    Button(root, text = 'Inference',width=8,height=2,command = Display2,font=('Arial', 15))\
           .grid(row = 20, column=0,sticky=E)
    Label(root,text = '---used to infer \n posts based \n on your input',font=('Arial', 10)).grid(row=21,column=0,sticky=E)
    Button(root, text = 'Quit',width=8,height=2,command = root.quit,font=('Arial', 15))\
           .grid(row = 23, column=0)
    root.mainloop()


def Display1():
    root1 = Toplevel()
    root1.title('Posts Generation')
    Label(root1,text = '###Please choose the source of posts you want to generate###',font=('Arial', 13)).grid(row=3,sticky=None)
    
    text = StringVar()
    v = IntVar()
    #r1 = Radiobutton(root1, variable = v, value=1, text="Hupu",font=("Arial", 16))
    r2 = Radiobutton(root1, variable = v, value=2, text="Zhihu",font=("Arial", 16))
    r3 = Radiobutton(root1, variable = v, value=3, text="Tieba",font=("Arial", 16))
    #r1.grid()
    r2.grid()
    r3.grid()

    def generate():
        word_list = ['我','你','他','这','太','那','额','也','不','。','哈','惊','却','但']
        text_start = random.choice(word_list)
        if v.get() == 1:
            text_generate = main(text_start,platform='hupu')
            #text_generate_new,_ = text_generate.rsplit('。',1)
            text.set(text_generate)
        elif v.get() == 2:
            text_generate = main(text_start,platform='zhihu')
            #text_generate_new,_ = text_generate.rsplit('。',1)
            text.set(text_generate)
        elif v.get() == 3:
            text_generate = main(text_start,platform='tieba')
            #text_generate_new,_ = text_generate.rsplit('。',1)
            text.set(text_generate)

    def Back():
        root1.destroy()
        root1.quit()

    Label(root1,text = '               ',font=('Arial', 15)).grid(sticky=None)
    label = Label(root1,textvariable = text, background = 'yellow',relief = 'ridge',font=('Arial', 15),
                fg = 'blue',height=10,width=40, wraplength=400, justify='left')
    label.grid()

    Label(root1,text = '               ',font=('Arial', 15)).grid(row=19,sticky=None)
    Button(root1, text = "Generate",width=8,height=2,command = generate,font=('Arial', 15))\
           .grid(row = 20, column = 0,sticky = W)
    Button(root1, text = 'Back',width=8,height=2,command = Back,font=('Arial', 15))\
           .grid(row = 20, column = 0, sticky = E)
    Button(root1, text = 'Quit',width=10,height=2,command = root1.quit,font=('Arial', 15))\
           .grid(row = 21, column = 0)
    root1.mainloop()


def Display2():
    root2 = Toplevel()
    root2.title('Posts Generation')
    Label(root2,text = '###Please input the sentence you want to infer###',font=('Arial', 15)).grid(row=1,sticky=None)
    Label(root2,text = '###It will give you the inference###',font=('Arial', 15)).grid(row=3,sticky=None)
    Label(root2,text = '               ',font=('Arial', 15)).grid(row=4,sticky=None)
    text = StringVar()
        
    Label(root2, text="Please input:",font=('Arial', 15)).grid(sticky=W)
    enter = Entry(root2,width=30,font=('Arial', 15))
    enter.grid()

    Label(root2,text = '###Please choose the source of posts you want to generate###',font=('Arial', 13)).grid(row=3,sticky=None)
    
    v = IntVar()
    #r1 = Radiobutton(root1, variable = v, value=1, text="Hupu",font=("Arial", 16))
    r2 = Radiobutton(root2, variable = v, value=1, text="Zhihu",font=("Arial", 16))
    r3 = Radiobutton(root2, variable = v, value=2, text="Tieba",font=("Arial", 16))
    #r1.grid()
    r2.grid()
    r3.grid()

    def generate():
        inputs = enter.get()
        if v.get() == 1:
            text_generate = main(inputs,'zhihu')
            #text_generate_new,_ = text_generate.rsplit('。',1)
        elif v.get() == 2:
            text_generate = main(inputs,'tieba')
            #text_generate_new,_ = text_generate.rsplit('。',1)
        text.set(str(text_generate))
    
    def Back():
        root2.destroy()
        root2.quit()
    
    Label(root2,text = '               ',font=('Arial', 15)).grid(sticky=None)
    label = Label(root2,textvariable = text, background = 'yellow',relief = 'ridge',font=('Arial', 15),
                fg = 'blue',height=10,width=40, wraplength=400, justify='left')
    label.grid()
    Label(root2,text = '               ',font=('Arial', 15)).grid(row=19,sticky=None)
    
    Button(root2, text = "Generate",width=8,height=2,command = generate,font=('Arial', 15))\
           .grid(row = 20, column = 0,sticky = W)
    Button(root2, text = 'Back',width=8,height=2,command = Back,font=('Arial', 15))\
           .grid(row = 20, column = 0, sticky = E)
    Button(root2, text = 'Quit',width=10,height=2,command = root2.quit,font=('Arial', 15))\
           .grid(row = 21, column = 0)
    root2.mainloop()

if __name__ == '__main__':
    Display()