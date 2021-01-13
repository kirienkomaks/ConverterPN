import tkinter as tk
from tkinter import ttk
import sqlite3
from converter import Converter


class DB:
    def __init__(self):
        self.conn_places = sqlite3.connect('ui_database/placesDB.db')
        self.c_places = self.conn_places.cursor()
        self.c_places.execute(
            '''CREATE TABLE IF NOT EXISTS places (id integer primary key, placeName text, marks text)''')
        self.conn_places.commit()

        self.conn_transitions = sqlite3.connect('ui_database/transitionsDB.db')
        self.c_transitions = self.conn_transitions.cursor()
        self.c_transitions.execute(
            '''CREATE TABLE IF NOT EXISTS transitions (id integer primary key, transitionName text, inputs text, outputs text)''')
        self.conn_transitions.commit()

    def insert_place_data(self, placeName, marks):
        self.c_places.execute('''INSERT INTO places(placeName, marks) VALUES (?, ?)''',
                              (placeName, marks))
        self.conn_places.commit()

    def insert_transition_data(self, transitionName, inputs, outputs):
        self.c_transitions.execute('''INSERT INTO transitions(transitionName, inputs, outputs) VALUES (?, ?, ?)''',
                                   (transitionName, inputs, outputs))
        self.conn_transitions.commit()


class Main(tk.Frame):
    def __init__(self, root):
        super().__init__(root)
        self.tree_place = ttk.Treeview(self, columns=('ID', 'placeName', 'marks'),
                                       height=10, show='headings')
        self.tree_transition = ttk.Treeview(self, columns=('ID', 'transitionName', 'inputs', 'outputs'),
                                            height=10, show='headings')
        self.init_main()
        self.db = db
        self.view_place_records()
        self.view_transition_records()
        self.places = []
        self.transitions = []

    def init_main(self):
        toolbar = tk.Frame(bg='#d7d8e0', bd=2)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        btn_open_dialog_place = tk.Button(toolbar, text='Add Place', command=self.open_dialog_place, bg='#d7d8e0',
                                          bd=0,
                                          compound=tk.TOP)
        btn_open_dialog_place.pack(side=tk.LEFT)

        btn_delete_place = tk.Button(toolbar, text='Delete Place', bg='#d7d8e0', bd=0,
                                     compound=tk.TOP, command=self.delete_place_records)
        btn_delete_place.pack(side=tk.LEFT)

        btn_update_place = tk.Button(toolbar, text='Update Place', bg='#d7d8e0', bd=0,
                                     compound=tk.TOP, command=self.open_update_place)
        btn_update_place.pack(side=tk.LEFT)

        btn_open_dialog_transition = tk.Button(toolbar, text='Add Transition', command=self.open_dialog_transition,
                                               bg='#d7d8e0', bd=0,
                                               compound=tk.TOP)
        btn_open_dialog_transition.pack(side=tk.LEFT)

        btn_update_transition = tk.Button(toolbar, text='Update Transition', bg='#d7d8e0', bd=0,
                                          compound=tk.TOP, command=self.open_update_transition)
        btn_update_transition.pack(side=tk.LEFT)

        btn_delete_transition = tk.Button(toolbar, text='Delete Transition', bg='#d7d8e0', bd=0,
                                          compound=tk.TOP, command=self.delete_transition_records)
        btn_delete_transition.pack(side=tk.LEFT)

        btn_create_pn = tk.Button(toolbar, text='Create PN Graph', command=self.create_pn, bg='#d7d8e0',
                                  bd=0,
                                  compound=tk.TOP)
        btn_create_pn.pack(side=tk.RIGHT)

        self.tree_place.column("ID", width=30, anchor=tk.CENTER)
        self.tree_place.column("placeName", width=365, anchor=tk.CENTER)
        self.tree_place.column("marks", width=150, anchor=tk.CENTER)

        self.tree_place.heading("ID", text='ID')
        self.tree_place.heading("placeName", text='Place Name')
        self.tree_place.heading("marks", text='Marks')

        self.tree_transition.column("ID", width=30, anchor=tk.CENTER)
        self.tree_transition.column("transitionName", width=215, anchor=tk.CENTER)
        self.tree_transition.column("inputs", width=150, anchor=tk.CENTER)
        self.tree_transition.column("outputs", width=150, anchor=tk.CENTER)

        self.tree_transition.heading("ID", text='ID')
        self.tree_transition.heading("transitionName", text='Transition Name')
        self.tree_transition.heading("inputs", text='Inputs')
        self.tree_transition.heading("outputs", text='Outputs')

        self.tree_place.pack()
        self.tree_transition.pack()

    def create_pn(self):
        self.places = []
        self.transitions = []
        self.db.c_places.execute('''SELECT * FROM places''')
        self.db.c_transitions.execute('''SELECT * FROM transitions''')
        for row in self.db.c_places.fetchall():
            self.places.append([row[1], row[2]])
        for row in self.db.c_transitions.fetchall():
            self.transitions.append([row[1], row[2].split(), row[3].split()])

        converter = Converter()
        converter.graphviz_formatter_ui(self.places, self.transitions)
        converter.places = len(self.places)
        converter.transitions = len(self.transitions)
        petri_net = converter.create_pn_UI()
        converter.write_pnml(petri_net, "pnml\\generated_ui.pnml")

    def records_place(self, placeName, marks):
        self.db.insert_place_data(placeName, marks)
        self.view_place_records()

    def records_transition(self, transitionName, inputs, outputs):
        self.db.insert_transition_data(transitionName, inputs, outputs)
        self.view_transition_records()

    def view_place_records(self):
        self.db.c_places.execute('''SELECT * FROM places''')
        [self.tree_place.delete(i) for i in self.tree_place.get_children()]
        [self.tree_place.insert('', 'end', values=row) for row in self.db.c_places.fetchall()]

    def view_transition_records(self):
        self.db.c_transitions.execute('''SELECT * FROM transitions''')
        [self.tree_transition.delete(i) for i in self.tree_transition.get_children()]
        [self.tree_transition.insert('', 'end', values=row) for row in self.db.c_transitions.fetchall()]

    def update_place_records(self, marks):
        self.db.c_places.execute('''UPDATE places SET marks = ? WHERE ID=?''',(marks, self.tree_place.set(self.tree_place.selection()[0], '#1')))
        self.db.conn_places.commit()
        self.view_place_records()

    def update_transition_records(self, inputs, outputs):
        self.db.c_transitions.execute('''UPDATE transitions SET inputs=?, outputs=?  WHERE ID=?''',
                          (inputs, outputs, self.tree_transition.set(self.tree_transition.selection()[0], '#1')))
        self.db.conn_transitions.commit()
        self.view_transition_records()

    def delete_place_records(self):
        for selection_item in self.tree_place.selection():
            self.db.c_places.execute('''DELETE FROM places WHERE id=?''', (self.tree_place.set(selection_item, '#1')))
        self.db.conn_places.commit()
        self.view_place_records()

    def delete_transition_records(self):
        for selection_item in self.tree_transition.selection():
            self.db.c_transitions.execute('''DELETE FROM transitions WHERE id=?''',
                                          (self.tree_transition.set(selection_item, '#1')))
        self.db.conn_transitions.commit()
        self.view_transition_records()

    @staticmethod
    def open_dialog_place():
        ChildPlace()

    @staticmethod
    def open_dialog_transition():
        ChildTransition()

    @staticmethod
    def open_update_place():
        UpdatePlace()

    @staticmethod
    def open_update_transition():
        UpdateTransition()


class ChildPlace(tk.Toplevel):
    def __init__(self):
        super().__init__(root)
        self.entry_place_marks = ttk.Entry(self)
        self.entry_place_name = ttk.Entry(self)
        self.label_place_name = tk.Label(self)
        self.view = app
        self.db = db
        self.count = 0
        self.get_places_count()
        self.init_child()

    def init_child(self):
        self.title('Add Place')
        self.geometry('250x140+400+300')
        self.resizable(False, False)

        self.label_place_name = tk.Label(self, text='Place  ' + str(self.count))
        self.label_place_name.place(x=10, y=20)
        label_place_marks = tk.Label(self, text='Marks')
        label_place_marks.place(x=10, y=50)

        self.entry_place_marks.place(x=100, y=50)

        btn_cancel = ttk.Button(self, text='Close', command=self.destroy)
        btn_cancel.place(x=140, y=100)

        btn_ok = ttk.Button(self, text='Add', command=self.destroy)
        btn_ok.place(x=30, y=100)
        btn_ok.bind('<Button-1>', lambda event: self.view.records_place("P" + str(self.count),
                                                                        self.entry_place_marks.get()), self.destroy)

        self.grab_set()
        self.focus_set()

    def get_places_count(self):
        self.db.c_places.execute('''SELECT * FROM places''')
        i = 0
        for row in self.db.c_places.fetchall():
            i += 1
        self.count = i


class ChildTransition(tk.Toplevel):
    def __init__(self):
        super().__init__(root)
        self.entry_transition_inputs = ttk.Entry(self)
        self.entry_transition_outputs = ttk.Entry(self)
        self.label_transition_name = tk.Label(self)
        self.view = app
        self.db = db
        self.count = 0
        self.get_transitions_count()
        self.init_child()

    def init_child(self):
        self.title('Add Transition')
        self.geometry('250x140+400+300')
        self.resizable(False, False)

        self.label_transition_name = tk.Label(self, text='Transition  ' + str(self.count))
        self.label_transition_name.place(x=10, y=10)
        label_transition_inputs = tk.Label(self, text='Inputs')
        label_transition_inputs.place(x=10, y=40)
        label_transition_outputs = tk.Label(self, text='Outputs')
        label_transition_outputs.place(x=10, y=60)

        self.entry_transition_inputs.place(x=100, y=40)

        self.entry_transition_outputs.place(x=100, y=60)

        btn_cancel = ttk.Button(self, text='Close', command=self.destroy)
        btn_cancel.place(x=140, y=100)

        btn_ok = ttk.Button(self, text='Add', command=self.destroy)
        btn_ok.place(x=30, y=100)
        btn_ok.bind('<Button-1>', lambda event: self.view.records_transition("t" + str(self.count),
                                                                             self.entry_transition_inputs.get(),
                                                                             self.entry_transition_outputs.get()))

        self.grab_set()
        self.focus_set()

    def get_transitions_count(self):
        self.db.c_transitions.execute('''SELECT * FROM transitions''')
        i = 0
        for row in self.db.c_transitions.fetchall():
            i += 1
        self.count = i


class UpdatePlace(ChildPlace):
    def __init__(self):
        super().__init__()
        self.init_edit()
        self.name=""
        self.view = app

    def init_edit(self):
        self.title('Update Place')
        self.name = self.view.tree_place.set(self.view.tree_place.selection()[0], '#2')
        self.label_place_name = tk.Label(self, text="Place to update: " + self.name)
        self.label_place_name.place(x=10, y=20)
        btn_edit = ttk.Button(self, text='Update Position', command=self.destroy)
        btn_edit.place(x=30, y=100)
        btn_edit.bind('<Button-1>', lambda event: self.view.update_place_records(self.entry_place_marks.get()), self.destroy)


class UpdateTransition(ChildTransition):
    def __init__(self):
        super().__init__()
        self.init_edit()
        self.view = app
        self.name = ""

    def init_edit(self):
        self.title('Update Transition')
        self.name = self.view.tree_transition.set(self.view.tree_transition.selection()[0], '#2')
        self.label_transition_name = tk.Label(self, text="Transition to update: " + self.name)
        self.label_transition_name.place(x=10, y=10)
        btn_edit = ttk.Button(self, text='Update Transition', command=self.destroy)
        btn_edit.place(x=30, y=100)
        btn_edit.bind('<Button-1>', lambda event: self.view.update_transition_records(self.entry_transition_inputs.get(),
                                                                                      self.entry_transition_outputs.get()), self.destroy)


if __name__ == "__main__":
    root = tk.Tk()
    db = DB()
    app = Main(root)
    app.pack()
    root.title("Petri Net PNML Constructor")
    root.geometry("650x450+300+200")
    root.resizable(False, False)
    root.mainloop()
