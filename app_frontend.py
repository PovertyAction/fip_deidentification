# Imports and Set-up
import sys
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.filedialog import askopenfilename, asksaveasfile
from PIL import ImageTk, Image
import os

import app_backend

app_title = "FIP Deidentification-Hashing App - v0.1"
intro_text = "- Hashing is designed for columns containing numbers (ex: msisdn)\n- DOB formatting is designed for columns with dates"

#Set parameters
window_width = 700
window_height = 700
max_screen = False
scrollbar = True

#Global variables
main_frame = None
file_imported = False
df_dict = None
columns_to_dropdown_element = {}

def display_title(title, frame):
    label = ttk.Label(frame, text=title, wraplength=546, justify=tk.LEFT, font=("Calibri", 12, 'bold'), style='my.TLabel')
    label.pack(anchor='nw', padx=(30, 30), pady=(0, 5))
    frame.update()
    return label

def display_message(message, frame):
    label = ttk.Label(frame, text=message, wraplength=546, justify=tk.LEFT, font=("Calibri Italic", 11), style='my.TLabel')
    label.pack(anchor='nw', padx=(30, 30), pady=(0, 5))
    frame.update()
    return label


def save_results(results_dict):
    file_types = [('Excel File', '*.xlsx')]
    saving_path = asksaveasfile(mode='wb', filetypes = file_types, defaultextension=".xlsx")

    result = app_backend.save_dataset(saving_path, results_dict)

    if(result):
        display_message("Saved. Bye!")

def check_column_format(column_name, action):
    print(column_name)
    print(action)

def display_columns(frame, columns, label_dict, default_dropdown_option="Keep"):

    columns_frame = tk.Frame(master=frame, bg="white")
    columns_frame.pack(anchor='nw', padx=(30, 30), pady=(0, 5))

    #Add title to grid
    ttk.Label(columns_frame, text='Column', wraplength=546, justify=tk.LEFT, font=("Calibri", 11, 'bold'), style='my.TLabel').grid(row=0, column = 0, sticky = 'w', pady=(0,2))
    ttk.Label(columns_frame, text='Desired action', wraplength=546, justify=tk.LEFT, font=("Calibri", 11, 'bold'), style='my.TLabel').grid(row=0, column = 1, sticky = 'w', padx=(5,0), pady=(0,2))

    #Display a label for each column and save their action dropdown element in dictionary for future reference
    for idx, column_name in enumerate(columns):

        #Given that in fist row of grid we have title of columns
        idx=idx+1

        #Add labels to pii candidates for better user understanding of column names
        if label_dict and column_name in label_dict and label_dict[column_name]!="":
            column_label = column_name + ": "+label_dict[column_name]+"\t"
        else:
            column_label = column_name+"\t"

        ttk.Label(columns_frame, text=column_label, wraplength=546, justify=tk.LEFT, font=("Calibri", 11), style='my.TLabel').grid(row=idx, column = 0, sticky = 'w', pady=(0,2))

        dropdown = tk.StringVar(columns_frame)

        option_menu = ttk.OptionMenu(columns_frame, dropdown, default_dropdown_option, "Drop", "Hash", "Keep", "DOB formatting",
        style='my.TMenubutton')

        option_menu.grid(row=idx, column = 1, sticky = 'w', pady=(0,2))

        columns_to_dropdown_element[column_name] = dropdown

    columns_frame.update()

    return columns_frame

def create_goodbye_frame(new_file_path):

    goodbye_frame = tk.Frame(master=main_frame, bg="white")
    goodbye_frame.pack(anchor='nw', padx=(0, 0), pady=(0, 0))

    if(new_file_path):
        display_title("Congratulations! Task ready!", goodbye_frame)
        display_message("The new dataset has been created and saved in "+new_file_path+".\nIf you hashed variables, you will also find hash_dictionary.csv that maps original to hashed values.\nYou will also find a log file describing the detection process.", goodbye_frame)

#PENDING: ADD A BUTTOM TO FOLDER WITH OUTPUTS

#PENDING: ENABLE RESTART PROGRAM
        # display_message("Do you want to work on a new file? Click Restart buttom.", goodbye_frame)
        # ttk.Button(goodbye_frame, text="Restart program", command=restart_program, style='my.TButton').pack(anchor='nw', padx=(30, 30), pady=(0, 5))


def create_deidentified_dataset(select_columns_frame):

    #We create a new dictionary that maps columns to actions based on value of dropdown elements
    columns_to_action = {}
    for column, dropdown_elem in columns_to_dropdown_element.items():
        columns_to_action[column] = dropdown_elem.get()

    #We need to check that selected actions are valid
    for column, action in columns_to_action.items():

        #Hash is only enabled for columns with numbers, check that
        if action == 'Hash':
            if(not app_backend.column_has_numbers(df_dict['dataset'], column)):
                messagebox.showinfo("Error", f'Column {column} has rows without numbers.\nHashing is only available for numbers.')
                return

        #For DOB formatting, column must be a date
        elif action == 'DOB formatting':
            if(not app_backend.column_has_dates(df_dict['dataset'], column)):
                messagebox.showinfo("Error", f'Column {column} has rows without dates.\nDOB formatting is only available for dates.')
                return


    display_message("Creating deidentified dataset...", select_columns_frame)

    #Automatic scroll down
    canvas.yview_moveto( 1 )
    main_frame.update()

    # global new_file_path



    new_file_path = app_backend.create_deidentified_dataset(df_dict['dataset'], df_dict['dataset_path'], columns_to_action)

    #Remove display of piis
    select_columns_frame.pack_forget()

    #Create final frame
    create_goodbye_frame(new_file_path)



def create_select_columns_frame(columns_names, labels_dict):

    select_columns_frame = tk.Frame(master=main_frame, bg="white")
    select_columns_frame.pack(anchor='nw', padx=(0, 0), pady=(0, 0))

    display_title('Columns:', select_columns_frame)

    if(len(columns_names)==0):
        display_message('No columns found.', select_columns_frame)
    else:
        display_message('For each column, select an action', select_columns_frame)
        display_columns(select_columns_frame, columns_names, labels_dict)


        create_deidentified_df_button = ttk.Button(select_columns_frame, text='Create deidentified dataset', command=lambda: create_deidentified_dataset(select_columns_frame), style='my.TButton')

        create_deidentified_df_button.pack(anchor='nw', padx=(30, 30), pady=(0, 5))
        # frame.update()

    return select_columns_frame

def import_file_and_start_process(first_view_frame):

    global df_dict
    global file_imported

    if(file_imported):
        return
    dataset_path = askopenfilename()

    #If no file was selected, do nothing
    if not dataset_path:
        return

    import_file_message = display_message("Importing File...", first_view_frame)

    import_succesfull, import_content = app_backend.import_dataset(dataset_path)
    if(import_succesfull):
        display_message("Dataset read successfully", first_view_frame)
        df_dict = import_content

        #Change file_imported status so as to disable new imports
        file_imported = True

        #Start processing df
        columns_names, labels_dict = app_backend.get_df_columns_names_and_labels(df_dict)

        #Remove current frame and create new one
        first_view_frame.pack_forget()

        select_columns_frame = create_select_columns_frame(columns_names, labels_dict)

    else:
        display_message("Error when importing dataset. Try again", frame)
        display_message(import_content, frame)

    import_file_message.pack_forget()

def window_setup(master):

    global window_width
    global window_height

    #Add window title
    master.title(app_title)

    #Add window icon
    if hasattr(sys, "_MEIPASS"):
        icon_location = os.path.join(sys._MEIPASS, 'app_icon.ico')
    else:
        icon_location = 'app_icon.ico'
    master.iconbitmap(icon_location)

    #Set window position and max size
    if(max_screen):
        window_width, window_height = master.winfo_screenwidth(), master.winfo_screenheight() # master.state('zoomed')?
    master.geometry("%dx%d+0+0" % (window_width, window_height))

    #Make window reziable
    master.resizable(True, True)


def window_style_setup(root):
    root.style = ttk.Style()
    root.style.configure('my.TButton', font=("Calibri", 11, 'bold'), background='white')
    root.style.configure('my.TLabel', background='white')
    root.style.configure('my.TCheckbutton', background='white')
    root.style.configure('my.TMenubutton', background='white')

def create_first_view_frame():

    first_view_frame = tk.Frame(master=main_frame, bg="white")
    first_view_frame.pack(anchor='nw', padx=(0, 0), pady=(0, 0))

    #Add intro text
    intro_text_label = ttk.Label(first_view_frame, text=intro_text, wraplength=746, justify=tk.LEFT, font=("Calibri", 11), style='my.TLabel')
    intro_text_label.pack(anchor='nw', padx=(30, 30), pady=(0, 12))

    #Labels and buttoms to run app
    start_application_label = ttk.Label(first_view_frame, text="Run application: ", wraplength=546, justify=tk.LEFT, font=("Calibri", 12, 'bold'), style='my.TLabel')
    start_application_label.pack(anchor='nw', padx=(30, 30), pady=(0, 10))

    select_dataset_button = ttk.Button(first_view_frame, text="Select Dataset",
    command=lambda : import_file_and_start_process(first_view_frame), style='my.TButton')
    select_dataset_button.pack(anchor='nw', padx=(30, 30), pady=(0, 5))

    return first_view_frame

def add_scrollbar(root, canvas, frame):

    #Configure frame to recognize scrollregion
    def onFrameConfigure(canvas):
        '''Reset the scroll region to encompass the inner frame'''
        canvas.configure(scrollregion=canvas.bbox("all"))

    frame.bind("<Configure>", lambda event, canvas=canvas: onFrameConfigure(canvas))

    def onMouseWheel(canvas, event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    #Bind mousewheel to scrollbar
    frame.bind_all("<MouseWheel>", lambda event, canvas=canvas: onMouseWheel(canvas, event))

    #Create scrollbar
    vsb = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=vsb.set)
    vsb.pack(side="right", fill="y")

if __name__ == '__main__':

    # Create GUI window
    root = tk.Tk()

    window_setup(root)

    window_style_setup(root)

    # Create canvas where app will displayed
    canvas = tk.Canvas(root, width=window_width, height=window_height, bg="white")
    canvas.pack(side="left", fill="both", expand=True)

    # Create frame inside canvas
    main_frame = tk.Frame(canvas, width=window_width, height=window_height, bg="white")
    main_frame.pack(side="left", fill="both", expand=True)

    #This create_window is related to the scrollbar.
    canvas.create_window(0,0, window=main_frame, anchor="nw")

    #Create Scrollbar
    if(scrollbar):
        add_scrollbar(root, canvas, main_frame)

    #Add IPA logo
    if hasattr(tk.sys, "_MEIPASS"):
        logo_location = os.path.join(sys._MEIPASS, 'ipa_logo.jpg')
    else:
        logo_location = 'ipa_logo.jpg'
    logo = ImageTk.PhotoImage(Image.open(logo_location).resize((147, 71), Image.ANTIALIAS))
    tk.Label(main_frame, image=logo, borderwidth=0).pack(anchor="nw", padx=(30, 30), pady=(30, 0))

    #Add app title
    app_title_label = ttk.Label(main_frame, text=app_title, wraplength=536, justify=tk.LEFT, font=("Calibri", 13, 'bold'), style='my.TLabel')
    app_title_label.pack(anchor='nw', padx=(30, 30), pady=(30, 10))

    #Create first view page
    first_view_frame = create_first_view_frame()

    # Constantly looping event listener
    root.mainloop()
