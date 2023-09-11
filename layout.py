import PySimpleGUI as sg


def get_layout():

    return [
        [sg.Text('Sélectionnez un répertoire contenant des fichiers SER :')],
        [sg.InputText(key='-FOLDER-',size=(70,200)), sg.FolderBrowse()],
        [sg.Checkbox('Include subdirectory', key='-SUBDIR-',default=False),sg.Checkbox('Delete originals', key='-DELETE-',default=False)],
        [sg.Text('Frames to keep (percent or number)'), sg.InputText(key="number",default_text='200')],
        [sg.Radio('Percentage', "TYPE", key='-OPTION_PERCENTAGE-', default=False, enable_events=True),sg.Radio('Number', "TYPE", key='-OPTION_NUMBER-', default=True,  enable_events=True)],
        [sg.Text('Suffix to add to filename'), sg.InputText(key="-SUFFIX-", default_text='_resized')],
        [sg.Button('GO')],
        [sg.Text('',  text_color='red', key='-ERROR-')],
        [sg.Text('',  text_color='blue', key='-TASKING-')],
        [sg.MLine(size=(100,20), write_only=True, expand_x=True, expand_y=True,key='-LOG-', reroute_cprint=True)],
    ]