import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import cv2
import os
import csv
import numpy as np
import pandas as pd
import datetime
import time
from PIL import ImageTk, Image

# Ensure a directory path exists
def assure_path_exists(path):
    os.makedirs(path, exist_ok=True)

# Check if the haarcascade file is present
def check_haarcascadefile():
    exists = os.path.isfile("haarcascade_frontalface_default.xml")
    if not exists:
        messagebox.showerror('File Missing', 'haarcascade_frontalface_default.xml is missing. Please contact support.')
        window.destroy()

# Function to take images for registration
def take_images():
    check_haarcascadefile()
    columns = ['SERIAL NO.', '', 'ID', '', 'NAME']
    assure_path_exists("StudentDetails/")
    assure_path_exists("TrainingImage/")
    serial = count_serial()
    exists = os.path.isfile("StudentDetails\StudentDetails.csv")
    if exists:
        with open("StudentDetails\StudentDetails.csv", 'r') as csvFile1:
            reader1 = csv.reader(csvFile1)
            for l in reader1:
                serial = serial + 1
        serial = (serial // 2)
        csvFile1.close()
    else:
        with open("StudentDetails\StudentDetails.csv", 'a+') as csvFile1:
            writer = csv.writer(csvFile1)
            writer.writerow(columns)
            serial = 1
        csvFile1.close()
    Id = (txt.get())
    name = (txt2.get())
    if name.replace(' ', '').isalpha():
        cam = cv2.VideoCapture(0)
        harcascadePath = "haarcascade_frontalface_default.xml"
        detector = cv2.CascadeClassifier(harcascadePath)
        sampleNum = 0
        while True:
            ret, img = cam.read()
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = detector.detectMultiScale(gray, 1.3, 5)
            for (x, y, w, h) in faces:
                cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
                sampleNum += 1
                cv2.imwrite("TrainingImage\ " + name + "." + str(serial) + "." + Id + '.' + str(sampleNum) + ".jpg",
                            gray[y:y + h, x:x + w])
                cv2.imshow('Taking Images', img)
            if cv2.waitKey(100) & 0xFF == ord('q') or sampleNum > 150:
                break
        cam.release()
        cv2.destroyAllWindows()
        res = "Images Taken for ID : " + Id
        row = [serial, '', Id, '', name]
        with open('StudentDetails\StudentDetails.csv', 'a+') as csvFile:
            writer = csv.writer(csvFile)
            writer.writerow(row)
        csvFile.close()
        message1.configure(text=res)
    else:
        res = "Enter Correct name"
        message.configure(text=res)

# Function to train images
def train_images():
    check_haarcascadefile()
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    harcascadePath = "haarcascade_frontalface_default.xml"
    detector = cv2.CascadeClassifier(harcascadePath)
    faces, ID = get_images_and_labels("TrainingImage")
    
    try:
        recognizer.train(faces, np.array(ID))
    except:
        messagebox.showerror('No Registrations', 'Please Register someone first!!!')
        return
    
    recognizer.save("TrainingImageLabel\Trainner.yml")
    res = "Profile Saved Successfully"
    message1.configure(text=res)
    message.configure(text=f'Total Registrations till now  : {ID[0]}')

# Function to get images and labels for training
def get_images_and_labels(path):
    imagePaths = [os.path.join(path, f) for f in os.listdir(path)]
    faces = []
    Ids = []
    for imagePath in imagePaths:
        pilImage = Image.open(imagePath).convert('L')
        imageNp = np.array(pilImage, 'uint8')
        ID = int(os.path.split(imagePath)[-1].split(".")[1])
        faces.append(imageNp)
        Ids.append(ID)
    return faces, Ids

# Function to take attendance
def track_images():
    check_haarcascadefile()
    assure_path_exists("Attendance/")
    assure_path_exists("StudentDetails/")
    for k in tv.get_children():
        tv.delete(k)
    
    msg = ''
    i = 0
    j = 0
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    exists3 = os.path.isfile("TrainingImageLabel\Trainner.yml")
    if exists3:
        recognizer.read("TrainingImageLabel\Trainner.yml")
    else:
        messagebox.showerror('Data Missing', 'Please click on save profile to reset data!!')
        return
    
    harcascadePath = "haarcascade_frontalface_default.xml"
    faceCascade = cv2.CascadeClassifier(harcascadePath)

    cam = cv2.VideoCapture(0)
    font = cv2.FONT_HERSHEY_SIMPLEX
    col_names = ['Id', '', 'Name', '', 'Date', '', 'Time']
    exists1 = os.path.isfile("StudentDetails\StudentDetails.csv")
    
    if exists1:
        df = pd.read_csv("StudentDetails\StudentDetails.csv")
    else:
        messagebox.showerror('Details Missing', 'Students details are missing, please check!')
        cam.release()
        cv2.destroyAllWindows()
        window.destroy()
    
    while True:
        ret, im = cam.read()
        gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(gray, 1.2, 5)
        for (x, y, w, h) in faces:
            cv2.rectangle(im, (x, y), (x + w, y + h), (225, 0, 0), 2)
            serial, conf = recognizer.predict(gray[y:y + h, x:x + w])
            if conf < 50:
                ts = time.time()
                date = datetime.datetime.fromtimestamp(ts).strftime('%d-%m-%Y')
                timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                aa = df.loc[df['SERIAL NO.'] == serial]['NAME'].values
                ID = df.loc[df['SERIAL NO.'] == serial]['ID'].values
                ID = str(ID)
                ID = ID[1:-1]
                bb = str(aa)
                bb = bb[2:-2]
                attendance = [str(ID), '', bb, '', str(date), '', str(timeStamp)]
            else:
                Id = 'Unknown'
                bb = str(Id)
            cv2.putText(im, str(bb), (x, y + h), font, 1, (255, 255, 255), 2)
        cv2.imshow('Taking Attendance', im)
        if cv2.waitKey(1) == ord('q'):
            break
    ts = time.time()
    date = datetime.datetime.fromtimestamp(ts).strftime('%d-%m-%Y')
    exists = os.path.isfile("Attendance\Attendance_" + date + ".csv")
    if exists:
        with open("Attendance\Attendance_" + date + ".csv", 'a+') as csvFile1:
            writer = csv.writer(csvFile1)
            writer.writerow(attendance)
        csvFile1.close()
    else:
        with open("Attendance\Attendance_" + date + ".csv", 'a+') as csvFile1:
            writer = csv.writer(csvFile1)
            writer.writerow(col_names)
            writer.writerow(attendance)
        csvFile1.close()
    with open("Attendance\Attendance_" + date + ".csv", 'r') as csvFile1:
        reader1 = csv.reader(csvFile1)
        for lines in reader1:
            i += 1
            if i > 1:
                if i % 2 != 0:
                    iidd = str(lines[0]) + '   '
                    tv.insert('', 0, text=iidd, values=(str(lines[2]), str(lines[4]), str(lines[6])))
    csvFile1.close()
    cam.release()
    
    # Adding a function to share attendance data as an Excel file
    def sharing():
        df_new = pd.read_csv('Attendance\Attendance_' + date + '.csv')
        GFG = pd.ExcelWriter('C:\\Users\\91809\\Downloads\\Attendance_project.xlsx')
        df_new.to_excel(GFG, index=False)
        GFG.save()
        cv2.destroyAllWindows()

global key
key = ''

ts = time.time()
date = datetime.datetime.fromtimestamp(ts).strftime('%d-%m-%Y')
day, month, year = date.split("-")

mont = {'01': 'JANUARY',
        '02': 'FEBRUARY',
        '03': 'MARCH',
        '04': 'APRIL',
        '05': 'MAY',
        '06': 'JUNE',
        '07': 'JULY',
        '08': 'AUGUST',
        '09': 'SEPTEMBER',
        '10': 'OCTOBER',
        '11': 'NOVEMBER',
        '12': 'DECEMBER'
        }

# GUI

window = tk.Tk()
window.geometry("1920x1080")
window.resizable(True,False)
window.title("E-ATTENDANCE SYSTEM")
window.configure(background='#29D823')

frame1 = tk.Frame(window, bg="#00aeff")
frame1.place(relx=0.10, rely=0.18, relwidth=0.35, relheight=0.70)

frame2 = tk.Frame(window, bg="#00aeff")
frame2.place(relx=0.54, rely=0.18, relwidth=0.35, relheight=0.70)

message3 = tk.Label(window, text="E-ATTENDANCE SYSTEM" ,fg="red",bg="#262523" ,width=55 ,height=1,font=('Arial Black', 29, ' bold '))
message3.place(x=10, y=10)

frame3 = tk.Frame(window, bg="#c4c6ce")
frame3.place(relx=0.52, rely=0.08, relwidth=0.09, relheight=0.07)

frame4 = tk.Frame(window, bg="#c4c6ce")
frame4.place(relx=0.36, rely=0.08, relwidth=0.16, relheight=0.07)

datef = tk.Label(frame4, text = day+"-"+mont[month]+"-"+year+"  |  ", fg="yellow",bg="#262523" ,width=55 ,height=1,font=('Cooper Black', 22, ' bold '))
datef.pack(fill='both',expand=1)

clock = tk.Label(frame3,fg="orange",bg="#262523" ,width=55 ,height=1,font=('Cooper Black', 22, ' bold '))
clock.pack(fill='both',expand=1)
tick()

head2 = tk.Label(frame2, text="\tFOR NEW REGISTRATION  \t\t", fg="black",bg="#3ece48" ,font=('Perpetua Titling MT', 18, ' bold ') )
head2.grid(row=0,column=0)

head1 = tk.Label(frame1, text="\tFOR ALREADY REGISTERED\t\t", fg="black",bg="#3ece48" ,font=('Perpetua Titling MT', 18, ' bold ') )
head1.place(x=0,y=0)

lbl = tk.Label(frame2, text="Enter ID",width=20  ,height=1  ,fg="black"  ,bg="#00aeff" ,font=('Cooper Black', 17, ' bold ') )
lbl.place(x=80, y=55)

txt = tk.Entry(frame2,width=32 ,fg="black",font=('times', 15, ' bold '))
txt.place(x=30, y=88)

lbl2 = tk.Label(frame2, text="Enter Name",width=20  ,fg="black"  ,bg="#00aeff" ,font=('Cooper Black', 17, ' bold '))
lbl2.place(x=80, y=140)

txt2 = tk.Entry(frame2,width=32 ,fg="black",font=('Cooper Black', 15, ' bold ')  )
txt2.place(x=30, y=173)

message1 = tk.Label(frame2, text="1)Take Image  >>>  2)Save Profile" ,bg="#00aeff" ,fg="black"  ,width=39 ,height=1, activebackground = "yellow" ,font=('Cooper Black', 15, ' bold '))
message1.place(x=7, y=230)

message = tk.Label(frame2, text="" ,bg="#00aeff" ,fg="black"  ,width=39,height=1, activebackground = "yellow" ,font=('Cooper Black', 16, ' bold '))
message.place(x=7, y=450)

lbl3 = tk.Label(frame1, text="ATTENDANCE ",width=20  ,fg="black"  ,bg="#00aeff"  ,height=1 ,font=('Cooper Black', 17, ' bold '))
lbl3.place(x=100, y=115)

res=0
exists = os.path.isfile("StudentDetails\StudentDetails.csv")
if exists:
    with open("StudentDetails\StudentDetails.csv", 'r') as csvFile1:
        reader1 = csv.reader(csvFile1)
        for l in reader1:
            res = res + 1
    res = (res // 2) - 1
    csvFile1.close()
else:
    res = 0
message.configure(text='Total Registrations till now  : '+str(res))

# MENU BAR

menubar = tk.Menu(window,relief='ridge')
filemenu = tk.Menu(menubar,tearoff=0)
filemenu.add_command(label='Change Password', command = change_pass)
filemenu.add_command(label='Contact Us', command = contact)
filemenu.add_command(label='Exit',command = window.destroy)
menubar.add_cascade(label='Help',font=('Cooper Black', 29, ' bold '),menu=filemenu)

# TREEVIEW ATTENDANCE TABLE

tv= ttk.Treeview(frame1,height =13,columns = ('NAME','DATE','TIME'))
tv.column('#0',width=82)
tv.column('NAME',width=130)
tv.column('DATE',width=133)
tv.column('TIME',width=133)
tv.grid(row=2,column=0,padx=(25,0),pady=(150,0),columnspan=4)
tv.heading('#0',text ='ID')
tv.heading('NAME',text ='NAME')
tv.heading('DATE',text ='DATE')
tv.heading('TIME',text ='TIME')

# SCROLLBAR

scroll=ttk.Scrollbar(frame1,orient='vertical',command=tv.yview)
scroll.grid(row=2,column=4,padx=(0,100),pady=(150,0),sticky='ns')
tv.configure(yscrollcommand=scroll.set)

# BUTTONS

clearButton = tk.Button(frame2, text="CLEAR", command=clear  ,fg="#FFFFFF"  ,bg="#C83DDA"  ,width=11 ,activebackground = "white" ,font=('Cooper Black', 11, ' bold '))
clearButton.place(x=335, y=86)
clearButton2 = tk.Button(frame2, text="CLEAR", command=clear2  ,fg="#FFFFFF"  ,bg="#C83DDA"  ,width=11 , activebackground = "white" ,font=('Cooper Black', 11, ' bold '))
clearButton2.place(x=335, y=172)    
takeImg = tk.Button(frame2, text="Take Images", command=TakeImages  ,fg="white"  ,bg="blue"  ,width=34  ,height=1, activebackground = "white" ,font=('Cooper Black', 15, ' bold '))
takeImg.place(x=30, y=300)
trainImg = tk.Button(frame2, text="Save Profile", command=psw ,fg="white"  ,bg="blue"  ,width=34  ,height=1, activebackground = "white" ,font=('Cooper Black', 15, ' bold '))
trainImg.place(x=30, y=380)
trackImg = tk.Button(frame1, text="Take Attendance", command=TrackImages  ,fg="black"  ,bg="yellow"  ,width=35  ,height=1, activebackground = "white" ,font=('Cooper Black', 15, ' bold '))
trackImg.place(x=30,y=50)
quitWindow = tk.Button(frame1, text="QUIT", command=window.destroy  ,fg="black"  ,bg="red"  ,width=35 ,height=1, activebackground = "white" ,font=('Cooper Black', 15, ' bold '))
quitWindow.place(x=30, y=450)

window.configure(menu=menubar)
window.mainloop()