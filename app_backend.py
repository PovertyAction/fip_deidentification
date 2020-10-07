import pandas as pd
import os
from hashlib import sha256
from datetime import datetime

LOG_FILE = None
OUTPUTS_PATH = None

def create_log_file_path(dataset_path):
    global LOG_FILE
    LOG_FILE = os.path.join(OUTPUTS_PATH, "log.txt")

def log_and_print(message):
    file = open(LOG_FILE, "a")
    file.write(message+'\n')
    file.close()
    print(message)

def open_hash_dictionary():
    #Read dictionary .csv file
    hash_dictionary_file = os.path.join(OUTPUTS_PATH,'hash_dictionary.csv')
    if os.path.exists(hash_dictionary_file):
        hash_dictionary_df = pd.read_csv(hash_dictionary_file)
        dict = pd.Series(hash_dictionary_df['hash'].values, index=hash_dictionary_df['value']).to_dict()
    else:
        print("No existing dict, creating new one")
        dict={}
    return dict

def column_has_numbers(df, col):

    #Clean column removing non-numbers
    df[col] = df[col].astype(str).str.extract('(\d+)', expand=False)

    #Check if there are any nulls after removal of numbers
    if(any(pd.isnull(df[col]))):
        return False
    else:
        return True

def column_has_dates(df, col):
    try:
        date_col = pd.to_datetime(df[col])
        #If any date is none, return false
        if(any(pd.isnull(date_col))):
            return False
        else:#If transformation was succesfull, return true
            return True
    #If there was an error transforming to date, return false
    except:
        return False

def generate_salt(value):
    #PENDING
    return 'xxxx'

def generate_hash_value(value):
    salt = generate_salt(value)
    hash_value = sha256((str(value)+salt).encode('utf-8')).hexdigest()
    return hash_value

def hash_dataframe_and_create_prefix_column(df, df_path, columns_to_hash, hash_dictionary):


    #We are expecting to hash only numeric columns
    for col in columns_to_hash:

        #Clean column removing non-numbers
        df[col] = df[col].astype(str).str.extract('(\d+)', expand=False)

        # Cut to last 9 digits of number
        # +254-yyy-xxxxxx, keep yyy-xxxxxx
        df[col] = df[col].str[-9:]

        #Create prefix column
        # +254-yyy-xxxxxx, yyy is carrier code prefix
        df[col+'_prefix'] = df[col].str[-9:-7].astype(int)

        #Change column type
        df[col] = df[col].astype(int)

        #Get all unique values and add them and their hash to hash_dict if they dont already exist
        for unique_val in df[col].unique():
            if unique_val not in hash_dictionary:
                hash_dictionary[unique_val] = generate_hash_value(unique_val)

        # Replace values for their hashes in dataframe
        # Loop over available values in the dictionary
        for k, v in hash_dictionary.items():
            df[col].replace(to_replace=k, value=v, inplace=True)

    return df, hash_dictionary

def get_parent_folder_path(dataset_path):
    return os.path.dirname(os.path.realpath(dataset_path))

def get_file_name(dataset_path):
    return dataset_path[dataset_path.rfind("/")+1:dataset_path.rfind(".")]

def export_hash_dict(hash_dict):

    hash_dict_file_path = os.path.join(OUTPUTS_PATH,'hash_dictionary.csv')

    #Delete if file exists to create a new one
    if os.path.exists(hash_dict_file_path):
        os.remove(hash_dict_file_path)

    hash_df = pd.DataFrame(columns=['value','hash'])

    for var, hash in hash_dict.items():
        hash_df.loc[-1] = [var, hash]
        hash_df.index = hash_df.index + 1

    hash_df.to_csv(hash_dict_file_path, index=False)

def dob_formatting(df, columns_for_dob_formatting):

    for col in columns_for_dob_formatting:
        date_parsed_col = pd.to_datetime(df[col])

        #If column indeed had dates
        if(any(date_parsed_col)):
            #Replace dob columns by years only
            year_col = date_parsed_col.dt.year.astype('int')
            df[col] = year_col

            # Aggregate all of those who were born in 1930 or earlier
            df.loc[df[col] < 1930, col] = 1930
    return df

def export_df(dataset, dataset_path):
    dataset_type = dataset_path.split('.')[1]
    file_name = get_file_name(dataset_path)

    new_file_path = os.path.join(OUTPUTS_PATH, file_name + '_deidentified.'+dataset_type)

    if(dataset_type == 'csv'):
        dataset.to_csv(new_file_path, index=False)

    elif(dataset_type == 'xlsx'):
        dataset.to_excel(new_file_path, index=False)

    elif(dataset_type == 'xls'):
        dataset.to_excel(new_file_path, index=False)
    else:
        log_and_print("Data type not supported")
        new_file_path = None

    return new_file_path

def all_dfs_have_same_columns(all_dfs_dict):
    #Columns of first df
    columns_first_df = all_dfs_dict[0]['dataset'].columns

    for index, df_dict in enumerate(all_dfs_dict):
        if index > 0: #We dont want to look at the first one
            #Check that all columns that are in the first df are in this df
            for c in columns_first_df:
                if c not in df_dict['dataset'].columns:
                    return False, f"Column {c}, found in {all_dfs_dict[0]['dataset_path']} is missing in {df_dict['dataset_path']}. Dataframes processed at the same time must have same columns"
    return True, "Success"



def create_deidentified_datasets(all_dfs_dict, columns_to_action):

    #Keep record of hashing
    hash_dictionary = open_hash_dictionary()

    for df_dict in all_dfs_dict:
        exported_file_path, hash_dictionary = create_deidentified_dataset(df_dict['dataset'], df_dict['dataset_path'], columns_to_action, hash_dictionary)

    #Export new dictionary
    export_hash_dict(hash_dictionary)


def create_deidentified_dataset(df, df_path, columns_to_action, hash_dictionary):
    ## a. Drops unneeded columns
    ## b. Hash columns so records can be matched across datasets, but holds on to number prefix to identify initial mobile carrier later
    ## c. Coverts date of birth to year of birth

    #Drop columns
    columns_to_drop = [column for column in columns_to_action if columns_to_action[column]=='Drop']
    if len(columns_to_drop)>0:
        df.drop(columns=columns_to_drop, inplace=True)
        log_and_print(f'Dropped columns: {" ".join(columns_to_drop)} in {df_path}')

    #Hash columns and keep prefixes
    columns_to_hash = [column for column in columns_to_action if columns_to_action[column]=='Hash']
    if(len(columns_to_hash)>0):
        df, hash_dictionary = hash_dataframe_and_create_prefix_column(df, df_path, columns_to_hash, hash_dictionary)
        log_and_print(f'Hashed columns: {" ".join(columns_to_hash)} in {df_path}')

    #DOB formatting
    columns_for_dob_formatting = [column for column in columns_to_action if columns_to_action[column]=='DOB formatting']
    if(len(columns_for_dob_formatting)>0):
        log_and_print("DOB formating for columns: "+ " ".join(columns_for_dob_formatting))
        df = dob_formatting(df, columns_for_dob_formatting)

    #Export new df
    exported_file_path = export_df(df, df_path)

    return exported_file_path, hash_dictionary

def get_df_columns_names_and_labels(df_dict):
    return df_dict['dataset'].columns, df_dict['label_dict']

def get_time_now_str():
    now = datetime.now()
    # dd/mm/YY H:M:S
    dt_string = now.strftime("%m_%d_%Y_%H_%M_%S")
    print("date and time =", dt_string)
    return dt_string

def create_outputs_folder(dataset_path):

    global OUTPUTS_PATH

    parent_folder_path = get_parent_folder_path(dataset_path)

    OUTPUTS_PATH = os.path.join(parent_folder_path, 'outputs_'+get_time_now_str())

    #Check that directory does not exist
    if os.path.isdir(OUTPUTS_PATH) is False:
        os.mkdir(OUTPUTS_PATH)


def import_datasets(datasets_path_list):

    create_outputs_folder(datasets_path_list[0])
    create_log_file_path(datasets_path_list[0])

    imports_result = []
    for dataset_path in datasets_path_list:
        import_succesfull, import_content = import_dataset(dataset_path)
        imports_result.append((import_succesfull, import_content))
    return imports_result

def import_dataset(dataset_path):

    dataset, label_dict, value_label_dict = False, False, False
    raise_error = False
    status_message = False

    #Check format
    if(dataset_path.endswith(('xlsx', 'xls','csv','dta')) is False):
        return (False, 'Supported files are .csv, .dta, .xlsx, .xls')

    try:
        if dataset_path.endswith(('xlsx', 'xls')):
            dataset = pd.read_excel(dataset_path)
        elif dataset_path.endswith('csv'):
            dataset = pd.read_csv(dataset_path)
        elif dataset_path.endswith('dta'):
            try:
                dataset = pd.read_stata(dataset_path)
            except ValueError:
                dataset = pd.read_stata(dataset_path, convert_categoricals=False)
            label_dict = pd.io.stata.StataReader(dataset_path).variable_labels()
            try:
                value_label_dict = pd.io.stata.StataReader(dataset_path).value_labels()
            except AttributeError:
                status_message = "No value labels detected. "
        elif dataset_path.endswith('vc'):
            status_message = f'**ERROR**: {dataset_path} appears to be encrypted using VeraCrypt.'
            raise Exception
        elif dataset_path.endswith('bc'):
            status_message = f'**ERROR**: This file {dataset_path} appears to be encrypted using Boxcryptor. Sign in to Boxcryptor and then select the file in your X: drive.'
            raise Exception
        else:
            raise Exception

    except (FileNotFoundError, Exception):
        if status_message is False:
            status_message = f'**ERROR**: {dataset_path} appears to be invalid.'
        raise

    if (status_message):
        log_and_print(f'There was an error reading {dataset_path}')
        log_and_print(status_message)
        return (False, status_message)

    log_and_print(f'The dataset {dataset_path} has been read successfully.')
    dataset_dict = {'dataset':dataset, 'dataset_path':dataset_path, 'label_dict':label_dict, 'value_label_dict':value_label_dict}
    return (True, dataset_dict)


# if __name__ == "__main__":
#
#     import_succesfull, import_content = import_dataset('fakedata.csv')
#
#     df_dict = import_content
#     columns_names, labels_dict = get_df_columns_names_and_labels(df_dict)
#
#     #Create fake options
#     columns_to_action = {}
#     for column in columns_names:
#         columns_to_action[column] = 'Keep'
#     columns_to_action['gender']='Hash'
#
#     columns_to_action['dob']='DOB formatting'
#
#     deidentified_df = create_deidentified_dataset(df_dict['dataset'],df_dict['dataset_path'], columns_to_action)
