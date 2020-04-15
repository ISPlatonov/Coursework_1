from tkinter import *
from tkinter import ttk
import sqlite3
import cv2
import os
import numpy as np
from PIL import Image
import main
import pandas as pd

root = Tk()

class Main(Frame):
    def __init__(self,master):
        super().__init__(master)
        self.proove()
        self.root_frame = Frame(master)
        self.root_frame.pack(expand = 1)
        self.btn_view = Button(self.root_frame,text = 'View from camera', width = 20, height = 7,command = self.open_view)
        self.btn_view.pack(expand = 1, pady = 10)
        
        self.btn_settings = Button(self.root_frame,text = 'Seetings',  width = 20, height = 5,command = self.open_settings)
        self.btn_settings.pack(expand = 1, pady = 10)
        
        self.btn_students = Button(self.root_frame, text = 'Students list',  width = 20, height = 7, command = self.open_students)
        self.btn_students.pack(expand = 1, pady = 10)
        
        self.btn_exitroot = Button(master, text = 'Exit', width = 10, command = self.exitroot)
        self.btn_exitroot.pack(side = BOTTOM, anchor = SE, pady = 20, padx = 20)
        
    def open_students(self):
        Students()
        
    def exitroot(self):
        root.destroy()
    
    def open_settings(self):
        Settings()
            
    def open_view(self):
        main.cam_2()
    #проверка корректности датасета
    def proove(self):
        import pandas as pd
        ex_list_id = [str(i) for i in pd.read_excel('ex_students.xlsx')['id']]
        path_ds = os.getcwd() + "/../dataset"
        list_photos = os.listdir(path_ds)
        #print(list_photos)
        for name in list_photos:
            if name.split('.')[1] not in ex_list_id:
                os.remove(path_ds + '/' + name)
        main.trainer_0()
        
class Settings(Toplevel):
    def __init__(self):
        super().__init__()
        data = pd.read_excel('ex_students.xlsx')
        self.title('Settings')
        self.geometry('700x450+{}+{}'.format(w,h))
        self.resizable(False,False)
        self.grab_set()
        self.focus_set()
        
        self.label_green = Label(self, text='Green phase')
        self.label_green.place(x = 70, y = 50)
        self.entry_green = ttk.Entry(self, width=5)
        self.entry_green.place(x=160, y=50)
        self.label_green_sec = Label(self, text='seconds')
        self.label_green_sec.place(x = 210, y = 50)
        
        self.label_red = Label(self, text='Red phase')
        self.label_red.place(x = 70, y = 80)
        self.entry_red = ttk.Entry(self, width=5)
        self.entry_red.place(x=160, y=80)
        self.label_red_sec = Label(self, text='seconds')
        self.label_red_sec.place(x = 210, y = 80)
        
        self.label_sdvig = Label(self, text='Phase shift')
        self.entry_sdvig = ttk.Entry(self,width=5)
        self.label_sdvig.place(x=70,y=110)
        self.entry_sdvig.place(x=160,y=110)
        self.label_sdvig_sec = Label(self, text='seconds')
        self.label_sdvig_sec.place(x = 210, y = 110)
        
        self.label_part = Label(self,text='Bottom part of screen for recognising')
        self.label_part.place(x=70,y=140)
        self.combobox_part = ttk.Combobox(self, values = ['20', '30','40', '50','60', '70','80'],width=5)
        for j in range(len(self.combobox_part['values'])):
            if str(int(data['Part'][0])) == self.combobox_part['values'][j]:
                self.combobox_part.current(j)
        self.combobox_part.place(x=285,y=140)
        self.label_percent = Label(self,text='%')
        self.label_percent.place(x=350,y=140)
    
        self.entry_sdvig.insert(0,data['Sdvig'][0])
        self.entry_green.insert(0,data['Green'][0]) 
        self.entry_red.insert(0,data['Red'][0])
        
        self.btn_save_set = Button(self,text='Save settings', width=10, command=self.save_settings)
        self.btn_save_set.place(x=150, y =170)
        
        self.btn_backfromset = Button(self, text = 'Back', width = 10, command = self.backfromset)
        self.btn_backfromset.pack(side = BOTTOM, anchor = SE, pady = 20, padx = 20)
    
    def save_settings(self):
        data = pd.read_excel('ex_students.xlsx')
        data['Green'][0] = self.entry_green.get()
        data['Red'][0] = self.entry_red.get()
        data['Sdvig'][0] = self.entry_sdvig.get()
        data['Part'][0] = self.combobox_part.get()
        data.to_excel('ex_students.xlsx', index = False)
        main.update_settings()
    
    def backfromset(self):
        self.destroy()
        
#окно с таблицей студентов        
class Students(Toplevel):
    def __init__(self):
        super().__init__()
        self.init_main()
        self.view_records() 
    
    def init_main(self):
        self.title('Students list')
        self.geometry('700x450+{}+{}'.format(w,h))
        self.resizable(False,False)
        self.grab_set()
        self.focus_set()
        #тулбар с функциональными кнопками
        self.toolbar = Frame(self, bg='#d7d8e0', bd='2')
        self.toolbar.pack(side = TOP,fill=X)
        
        btn_opendialog = Button(self.toolbar,text='Add student', bg='#d7d8e0', bd='2',command=self.open_dialog,compound = TOP)
        btn_opendialog.pack(side = LEFT)
        
        btn_edit_dialog = Button(self.toolbar, text='Edit profile',bg='#d7d8e0', bd='2', command  = self.open_updatedialog,compound = TOP)
        btn_edit_dialog.pack(side = LEFT)
        
        btn_delete_info = Button(self.toolbar, text='Delete student', bg='#d7d8e0', bd='2',command =self.delete_info, compound = TOP)
        btn_delete_info.pack(side = LEFT)
        
        self.tree = ttk.Treeview(self, column=('id','name','email','date','number', 'groups', 'devs'), 
                                 height = 15, show = 'headings') 
        #описываем колонки таблички
        self.tree.column('id',width=30,anchor=CENTER)
        self.tree.column('name',width=130,anchor=CENTER)
        self.tree.column('email',width=130,anchor=CENTER)
        self.tree.column('date',width=100,anchor=CENTER)
        self.tree.column('number',width=100,anchor=CENTER)
        self.tree.column('groups',width=50,anchor=CENTER)
        self.tree.column('devs',width=80,anchor=CENTER)
        
        #даем колонкам заголовки
        self.tree.heading('id',text='id')
        self.tree.heading('name',text='Name')
        self.tree.heading('email',text='Email')
        self.tree.heading('date',text='Birth date')
        self.tree.heading('number',text='Number')
        self.tree.heading('groups',text='Group')
        self.tree.heading('devs',text='Deviations')
        
        self.tree.pack(side= LEFT, padx=20, anchor = N)
        
        scroll = Scrollbar(self,command=self.tree.yview)
        scroll.pack(side=RIGHT,fill=Y)
        self.tree.config(yscrollcommand=scroll.set)
        
        self.btn_backroot = Button(self, text = 'Back', width =10, command = self.backtoroot)
        self.btn_backroot.place(x = 600, y = 415)
    
    def backtoroot(self):
        self.destroy()
        
    #функция отображения информации из эксель в виджете treе, удаляем старые данные, и заполняем новыми, импортируя их из бд
    def view_records(self):
        [self.tree.delete(i) for i in self.tree.get_children()] 
        data = pd.read_excel('ex_students.xlsx') 
        data_matrix = []
        local=[]
        for i in range(len(data['Name'])):
            local = []
            for j in data.columns:
                local.append(data[j][i])
            data_matrix.append(local)
        [self.tree.insert('','end', values = row ) for row in data_matrix]
    
    #функция удаления строки в экселе
    def delete_info(self):
        data = pd.read_excel('ex_students.xlsx')
        treeid = self.tree.selection()[0] #внутренний id в treeview
        for i in range(len(data['Name'])):
            if data['Name'][i] == self.tree.item(treeid, option="values")[1]: #получаем значение из treeview
                data = data.drop(i)
        data.to_excel('ex_students.xlsx', index = False)
        #удаление фотографий
        del_id = self.tree.item(treeid, option="values")[0]
        #print(del_id)
        path_ds = os.getcwd() + "/../dataset"
        list_photos = os.listdir(path_ds)
        #print(list_photos)
        for name in list_photos:
            if name.split('.')[1] == str(del_id):
                os.remove(path_ds + '/' + name)
        #отображаем изменения и заново обучаем
        self.view_records()
        main.trainer_0()
        
    #вызываем дочернее окно
    def open_dialog(self):
        Students.destroy(self)
        AddStudent()
        
    #вызываем окно редактирования    
    def open_updatedialog(self):
        self.destroy()
        Update()
        
        
class AddStudent(Toplevel):
    def __init__(self):
        super().__init__()
        self.title('Add student')
        self.geometry('700x450+{}+{}'.format(w,h))
        self.resizable(False,False)
        
        #подписи к виджетам
        self.label_id = Label(self, text='id')
        self.label_id.place(x = 50, y = 50)
        self.label_name = Label(self, text='Name')
        self.label_name.place(x = 50, y = 80)
        self.label_email = Label(self, text='Email')
        self.label_email.place(x = 50, y = 110)
        self.label_date = Label(self, text='Birth date')
        self.label_date.place(x = 50, y = 140)
        self.label_number = Label(self, text='Number')
        self.label_number.place(x = 50, y = 170)
        self.label_groups = Label(self, text='Group')
        self.label_groups.place(x = 50, y = 200)
        self.label_devs = Label(self, text='Deviations')
        self.label_devs.place(x = 50, y = 230)
        self.label_add = Label(self, text = 'Please look at the camera after adding student until ending Capture programm')
        self.label_add.place(x = 50, y = 20)
        
        #виджеты ввода
        data = pd.read_excel('ex_students.xlsx')
        #подставляем исходный id
        self.label_id_entry = Label(self, text=int(data['id'][len(data['id'])-1]+1))
        self.label_id_entry.place(x = 200, y = 50)
        
        self.entry_name = ttk.Entry(self)
        self.entry_name.place(x=200, y=80)
        
        self.entry_email = ttk.Entry(self)
        self.entry_email.place(x=200, y=110)
        
        self.entry_date = ttk.Entry(self)
        self.entry_date.place(x=200, y=140)
        
        self.entry_number = ttk.Entry(self)
        self.entry_number.place(x=200, y=170)
        
        self.combobox = ttk.Combobox(self, values = ['БИВ191', 'БИВ192','БИВ193', 'БИВ194','БИВ195', 'БИВ196','БИВ197'])
        self.combobox.current(1) 
        self.combobox.place(x=200,y=200)
        
        self.entry_devs = ttk.Entry(self)
        self.entry_devs.place(x=200, y=230)
        
        #кнопка закрытия дочернего окна
        self.btn_cancel = ttk.Button(self,text='Back')
        self.btn_cancel.bind('<Button-1>', lambda event: self.vspom()) 
        self.btn_cancel.place(x = 300, y = 280)
        
        #кнопка добавления информации введенной через виджеты
        self.btn_ok = ttk.Button(self, text='Add')
        self.btn_ok.place(x = 200, y = 280)
        self.btn_ok.bind('<Button-1>', lambda event: self.records())
        self.grab_set()
        self.focus_set()
    def vspom(self):
        self.destroy()
        Students()
    #запись нового студента
    def records(self):
        data = pd.read_excel('ex_students.xlsx')
        data = data.append({'id':int(data['id'][len(data['id'])-1]+1),'Name':self.entry_name.get(), 'Email':self.entry_email.get(), 'Birth Date':self.entry_date.get(),'Number':self.entry_number.get(), 'Group':self.combobox.get(), 'Deviations':self.entry_devs.get()}, ignore_index=True)
        data.to_excel('ex_students.xlsx', index = False)
        print(data['id'][len(data['id']) - 1])  #id добавляемого
        main.cam_1(data['id'][len(data['id']) -1])
    
class Update(AddStudent):
    def __init__(self):
        super().__init__()
        self.init_edit()
        self.label_add.destroy()
    
    def init_edit(self):
        #блок из комбобокса ентри и кнопки для поиска студентов
        self.combobox_search = ttk.Combobox(self, values = ['Search by Email', 'Search by Name','Search by id'])
        self.combobox_search.current(1) 
        self.combobox_search.place(x=50,y=50)
        
        self.entry_search = ttk.Entry(self)
        self.entry_search.place(x=200, y=50)
        
        self.btn_find =Button(self,text='Find', command = self.find,width =10) 
        self.btn_find.place(x =350 , y = 50)
        
        self.label_id.place(x = 50, y = 80)
        self.label_name.place(x = 50, y = 110)
        self.label_email.place(x = 50, y = 140)
        self.label_date.place(x = 50, y = 170)
        self.label_number.place(x = 50, y = 200)
        self.label_groups.place(x = 50, y = 230)
        self.label_devs.place(x = 50, y = 260)
        #вставка/редактирование информации о найденном студенте
        self.label_id_entry.place(x = 200, y = 80)
        self.entry_name.place(x = 200, y =110)
        self.entry_email.place(x = 200, y = 140)
        self.entry_date.place(x = 200, y = 170)
        self.entry_number.place(x = 200, y = 200)
        self.combobox.place(x = 200, y = 230)
        self.entry_devs.place(x = 200, y = 260)
        
        self.title('Edit profile')
        #кнопка редактирования данных
        btn_edit = ttk.Button(self,text = 'Edit', width = 10)
        btn_edit.place(x = 200, y = 310)
        btn_edit.bind('<Button-1>', lambda event: self.update_records())
        self.btn_ok.destroy()
        self.btn_cancel.place(x = 300, y = 310)
        
        self.label_id_entry = Label(self, text = 'Unknown')
        self.label_id_entry.place(x = 200, y = 80)
        
        #self.label_find = Label(self, text='Search student by email')
        #self.label_find.place(x = 350, y = 80)
        
        
    #находим по id/имени/почте студента и вставляем его данные в entry_
    def find(self):
        #верхний поисковой блок студента
        if self.combobox_search.get() == 'Search by id':
            self.search_string = 'id'
        if self.combobox_search.get() == 'Search by Name':
            self.search_string = 'Name'
        if self.combobox_search.get() == 'Search by Email':
            self.search_string = 'Email'
            
        #удаляем старые данные
        self.entry_name.delete(0, 'end')
        self.entry_email.delete(0, 'end')
        self.entry_date.delete(0, 'end')
        self.entry_number.delete(0, 'end')
        self.entry_devs.delete(0, 'end')    
        
        #вставляем данные найденного студента    
        data = pd.read_excel('ex_students.xlsx')
        for i in range(len(data[self.search_string])):
            if str(data[self.search_string][i]) == self.entry_search.get():
                self.label_id_entry['text'] = data['id'][i]
                self.entry_name.insert(0,data['Name'][i])
                self.entry_email.insert(0, data['Email'][i])
                self.entry_date.insert(0,data['Birth Date'][i]) 
                self.entry_number.insert(0,data['Number'][i]) 
                self.entry_devs.insert(0,data['Deviations'][i])
                for j in range(len(self.combobox['values'])):
                    if data['Group'][i] == self.combobox['values'][j]:
                        self.combobox.current(j)

                
    #запись в эксель релактированной информации
    def update_records(self):
        data = pd.read_excel('ex_students.xlsx')
        for i in range(len(data['Name'])):
            if str(data['id'][i]) == self.label_id_entry['text']:
                data['Name'][i] = self.entry_name.get()
                data['Email'][i] = self.entry_email.get()
                data['Birth Date'][i] = self.entry_date.get()
                data['Number'][i] = self.entry_number.get()
                data['Group'][i] = self.combobox.get()
                data['Deviations'][i] = self.entry_devs.get()
                data.to_excel('ex_students.xlsx', index = False)
                
        
        

w = root.winfo_screenwidth() // 2 - 325
h = root.winfo_screenheight() // 2 - 225
appmain = Main(root)
appmain.pack()
root.title('Recognising system')
root.geometry('700x450+{}+{}'.format(w,h))
root.resizable(False, False)
root.mainloop()
'''records и update_records прописаны в классах дочерних окон и вызываются из этих же классов.
когда закрываются дочерние окна, заново открывается окно Students, при открытии которого выполняется
view_records показывающие в таблице текущие данные в экселе.
окно Students закрывается при нажатии на Add student или Edit'''


