# IK: This file is intended to house some common functions and modules
# used by all of the eye-tracking data processing scripts
# this way we ensure that recurring tasks (like writing to files) aren't
# duplicated in several files but instead stored and defined in just one.

# import module for OS interaction
import os, re, csv
# import regular expressions
import re
# import table file writing module
import csv
# import readline and set tab-completion based on what OS we are in
import readline
# MACOS uses "libedit" for readline functionality and has a different command
# for enabling tab completion
if 'libedit' in readline.__doc__:
    readline.parse_and_bind("bind ^I rl_complete")
# whereas Unix (and maybe Windows) have the same command
else:
    readline.parse_and_bind("tab: complete")

###############################################################################
## Functions for interacting with users
###############################################################################

def ask_user_questions(question_sequence, use_template=True, return_list=False):
    '''Given a sequence of items (can be a list or a dictionary, anything
    that supports iteration), prints prompts for every item in the shell
    so that the user can input a value for every item.
    Returns a dictionary of (item_name : user_input) pairings.
    '''
    # define question prompt template and return variable
    q_template = 'Please enter the {} below:\n'

    if use_template:
        question_strings = [q_template.format(q) for q in question_sequence]
        answers = [input(question) for question in question_strings]
    else:
        answers = [input(question) for question in question_sequence]
    if return_list:
        return answers
    return dict(zip(question_sequence, answers))


def ask_single_question(question):
    return ask_user_questions([question], 
        use_template=False, 
        return_list=True)[0]


# define regular expression that checks for "yes" answers
_YES_RGX = re.compile('y(:?e[sa]|up)?', re.IGNORECASE)

def is_yes(user_input):
    return bool(_YES_RGX.match(user_input))

###############################################################################
## Functions for dealing with file names/paths
###############################################################################

def is_DA1_file(filename):
    '''Checks if a file name has DA1 extension.
    Currently accepts both ".da1" and ".DA1" files.
    Retunrs a boolean (True or False).
    '''
    return filename.endswith('.da1') or filename.endswith('.DA1')


_SUBJ_N_RGX = re.compile('\d+')


def get_subj_num(file_path):
    '''Given a filename string returns any substring that consists of digits.
    If multiple such substrings are found, returns the first one.
    If no such substrings are found, returns empty string and warns the user.
    '''
    # first we make sure we're dealing with file's name, not full path to it
    file_name = os.path.basename(file_path)
    # we don't want to risk finding digits from file extensions
    extensionless = file_name.split('.')[0]
    matches = _SUBJ_N_RGX.findall(extensionless)

    if not matches:
        warning = "Unable to find subject number in this file name: \n{0}"
        print(warning.format(file_name))
        return ''

    elif len(matches) > 1:
        warning = "Found several numbers in '{0}', using the first one out of: \n{1}"
        print(warning.format(file_name, matches))

    return matches[0]


def gen_file_paths(dir_name, filter_func=None):
    if filter_func:
        return (os.path.join(dir_name, file_name) 
            for file_name in os.listdir(dir_name)
            if filter_func(file_name))
    
    return (os.path.join(dir_name, file_name) for file_name in os.listdir(dir_name))


###############################################################################
## Functions for writing to files
###############################################################################

def create_row_dict(fields, item, fill_val='NA'):
    length_difference = len(fields) - len(item)
    error_message = 'There are more items than labels for them: {0}'
    if length_difference < 0:
        print('Here are the column labels', fields)
        print('Here are the items', item)
        raise Exception(error_message.format(length_difference))
    elif length_difference > 0:
        item = item + (fill_val,) * length_difference

    return dict(zip(fields, item))


def write_to_table(file_name, data, header=None, **kwargs):
    '''Writes data to file specified by filename.

    :type file_name: string
    :param file_name: name of the file to be created
    :type data: iterable
    :param data: some iterable of dictionaries each of which
    must not contain keys absent in the 'header' argument
    :type header: list
    :param header: list of columns to appear in the output
    :type **kwargs: dict
    :param **kwargs: parameters to be passed to DictWriter.
    For instance, restvals specifies what to set empty cells to by default or
    'dialect' loads a whole host of parameters associated with a certain csv
    dialect (eg. "excel").
    '''
    with open(file_name, 'w') as f:
        if header:
            output = csv.DictWriter(f, header, **kwargs)
            output.writeheader()
            data = (create_row_dict(row) for row in data)
        else:
            output = csv.writer(f, **kwargs)
        output.writerows(data)
