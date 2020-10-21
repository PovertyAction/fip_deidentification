# Imports and Set-up
import sys
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.filedialog import asksaveasfile, askopenfilenames
from PIL import ImageTk, Image
import os

import app_backend

app_title = "FIP Deidentification-Hashing App - v0.2"
intro_text = "- Hashing is designed for columns containing numbers (ex: msisdn)\n- DOB formatting is designed for columns with dates\n- You can choose either one or multiple files for deidentification.\nIf you choose multiple, all files are expected to have the same format (columns)."

#Set parameters
window_width = 700
window_height = 700
max_screen = False
scrollbar = True

#Global variables
main_frame = None
files_read_frame = None
all_dfs_dict = None
password = None
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

def create_goodbye_frame(outputs_folder):

    goodbye_frame = tk.Frame(master=main_frame, bg="white")
    goodbye_frame.pack(anchor='nw', padx=(0, 0), pady=(0, 0))


    display_title("Congratulations! Task ready!", goodbye_frame)
    display_message(f"The new deidentified datasets have been created.\nYou can find all outputs in {outputs_folder}\nIf you hashed variables, you will find hash_dictionary.csv that maps original to hashed values.\nYou will also find a log file describing the deidentification process.", goodbye_frame)

#PENDING: ADD A BUTTOM TO FOLDER WITH OUTPUTS

#PENDING: ENABLE RESTART PROGRAM
        # display_message("Do you want to work on a new file? Click Restart buttom.", goodbye_frame)
        # ttk.Button(goodbye_frame, text="Restart program", command=restart_program, style='my.TButton').pack(anchor='nw', padx=(30, 30), pady=(0, 5))


def selected_actions_are_valid(columns_to_action):
    for df_dict in all_dfs_dict:
        for column, action in columns_to_action.items():
            #Hash is only enabled for columns with numbers, check that
            if action == 'Hash':
                print(df_dict['dataset_path'])
                if(not app_backend.column_has_numbers(df_dict['dataset'], column)):
                    print(df_dict.keys())
                    messagebox.showinfo("Error", f"Column {column} in {df_dict['dataset_path']} has rows without numbers.\nHashing is only available for numbers.")
                    return False
            #For DOB formatting, column must be a date
            elif action == 'DOB formatting':
                column_has_dates_result = app_backend.column_has_dates(df_dict['dataset'], column)

                if column_has_dates_result == 'SOME EMPTY VALUES':
                    messagebox.showinfo("Warning", f"Column {column} in {df_dict['dataset_path']} has rows with empty values.\nThese observations will contain missing Year of Birth information.")
                elif column_has_dates_result == 'ALL EMPTY VALUES':
                    messagebox.showinfo("Error", f"Column {column} in {df_dict['dataset_path']} has all rows with empty values.\nChoose a different column for DOB formatting.")
                    return False
                elif column_has_dates_result == 'ERROR':
                    messagebox.showinfo("Error", f"Column {column} in {df_dict['dataset_path']} has rows without date formats.\nChoose a different column for DOB formatting.")
                    return False

    return True



def create_deidentified_datasets(select_columns_frame):

    #We create a new dictionary that maps columns to actions based on value of dropdown elements
    columns_to_action = {}
    for column, dropdown_elem in columns_to_dropdown_element.items():
        columns_to_action[column] = dropdown_elem.get()

    #We need to check that selected actions are valid
    if(not selected_actions_are_valid(columns_to_action)):
        return

    display_message("Creating deidentified dataset(s)...", select_columns_frame)

    #Automatic scroll down
    canvas.yview_moveto( 1 )
    main_frame.update()

    outputs_path = app_backend.create_deidentified_datasets(all_dfs_dict, columns_to_action, password)

    #Remove current frame
    select_columns_frame.pack_forget()

    #Create final frame
    create_goodbye_frame(outputs_path)



def create_select_columns_frame(first_view_frame):

    #We need to check that all selected dfs have same structure
    all_columns_same_names, error_message = app_backend.all_dfs_have_same_columns(all_dfs_dict)
    if(not all_columns_same_names):
      messagebox.showinfo("Error", error_message)
      return

    #Remove current frame
    first_view_frame.pack_forget()

    #Get columns
    columns_names, labels_dict = app_backend.get_df_columns_names_and_labels(all_dfs_dict[0])

    select_columns_frame = tk.Frame(master=main_frame, bg="white")
    select_columns_frame.pack(anchor='nw', padx=(0, 0), pady=(0, 0))

    display_title('Columns:', select_columns_frame)

    if(len(columns_names)==0):
        display_message('No columns found.', select_columns_frame)
    else:
        display_message('For each column, select an action', select_columns_frame)
        display_columns(select_columns_frame, columns_names, labels_dict)


        create_deidentified_df_button = ttk.Button(select_columns_frame, text='Create deidentified dataset(s)', command=lambda: create_deidentified_datasets(select_columns_frame), style='my.TButton')

        create_deidentified_df_button.pack(anchor='nw', padx=(30, 30), pady=(0, 5))
        # frame.update()

    return select_columns_frame

def update_files_read_frame(first_view_frame):
    global files_read_frame

    #Clean previous files read
    if(files_read_frame is not None):
        files_read_frame.pack_forget()

    #Display files read
    if(len(all_dfs_dict))>0:
        files_read_frame = tk.Frame(master=first_view_frame, bg="white")
        files_read_frame.pack(anchor='nw', padx=(0, 0), pady=(0, 0))

        display_message("Success reading following file(s):", files_read_frame)
        for df_dict in all_dfs_dict:
            display_message(df_dict['dataset_path'], files_read_frame)

        #Add buttom to start deidentification
        deidentify_button = ttk.Button(files_read_frame, text="Start deidentification",
        command=lambda : create_select_columns_frame(first_view_frame), style='my.TButton')
        deidentify_button.pack(anchor='nw', padx=(30, 30), pady=(0, 5))


def import_files(first_view_frame):

    global all_dfs_dict

    datasets_path = list(askopenfilenames())

    #If no file was selected, do nothing
    if not datasets_path or len(datasets_path)==0:
        return

    import_file_message = display_message("Importing File(s)...", first_view_frame)

    imports_result = app_backend.import_datasets(datasets_path)
    import_file_message.pack_forget()

    all_dfs_dict = []

    #Check imports of different files result
    for import_result in imports_result:
        import_succesfull, import_content = import_result

        if not import_succesfull:
            messagebox.showinfo("Error when importing dataset", import_content)
        else:
            all_dfs_dict.append(import_content)

    update_files_read_frame(first_view_frame)


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

def check_password(password_inserted, first_view_frame, password_frame):
    global password

    password_is_correct = app_backend.check_password(password_inserted)

    if password_is_correct:
        messagebox.showinfo("Success", f"Welcome, you are logged in")
        password = password_inserted

        #Remove password frame
        password_frame.pack_forget()

        #Labels and buttoms to run app
        start_application_label = ttk.Label(first_view_frame, text="Run application: ", wraplength=546, justify=tk.LEFT, font=("Calibri", 12, 'bold'), style='my.TLabel')
        start_application_label.pack(anchor='nw', padx=(30, 30), pady=(0, 10))

        select_dataset_button = ttk.Button(first_view_frame, text="Select Dataset(s)",
        command=lambda : import_files(first_view_frame), style='my.TButton')
        select_dataset_button.pack(anchor='nw', padx=(30, 30), pady=(0, 5))

    else:
        messagebox.showinfo("Error", f"Wrong password, please try again")
        return False


def create_password_frame(first_view_frame):

    password_frame = tk.Frame(master=first_view_frame, bg="white")
    password_frame.pack(anchor='nw', padx=(0, 0), pady=(0, 0))

    password_label = ttk.Label(password_frame, text="Password to run app: ", wraplength=546, justify=tk.LEFT, font=("Calibri", 12, 'bold'), style='my.TLabel')
    password_label.pack(anchor='nw', padx=(30, 30), pady=(0, 10))

    password_entry = tk.Entry(password_frame)
    password_entry.pack(anchor='nw', padx=(30, 30), pady=(0, 10))

    check_password_button = ttk.Button(password_frame, text="Log in",
    command=lambda : check_password(password_entry.get(), first_view_frame, password_frame), style='my.TButton')
    check_password_button.pack(anchor='nw', padx=(30, 30), pady=(0, 5))

    return password_frame

def create_first_view_frame():

    first_view_frame = tk.Frame(master=main_frame, bg="white")
    first_view_frame.pack(anchor='nw', padx=(0, 0), pady=(0, 0))

    #Add intro text
    intro_text_label = ttk.Label(first_view_frame, text=intro_text, wraplength=746, justify=tk.LEFT, font=("Calibri", 11), style='my.TLabel')
    intro_text_label.pack(anchor='nw', padx=(30, 30), pady=(0, 12))

    #Labels and buttoms to check password
    password_frame = create_password_frame(first_view_frame)

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
