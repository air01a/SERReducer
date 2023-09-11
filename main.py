from layout import get_layout
import PySimpleGUI as sg
from reduceser import ReduceSer

class CallBack:
    def __init__(self, window):
        self.window = window
    
    def callback(self,message):
        if message=='+FINISHED+':
            self.window.write_event_value('-TASKFINISH-','')

        

def run():
    reduce_ser = None
    
    sg.theme('Black')
    #(height,width)=get_window_size()
    layout = get_layout()
    observer = None

    window = sg.Window('SER Reducer [easyastro]', layout, finalize=True, element_justification='c',resizable=True,default_element_size=(12, 1))
    callback = CallBack(window)
    while True:
        event, values = window.read()

        if event == sg.WINDOW_CLOSED or event == 'Quitter':
            break
        elif event == '-LOGUPDATE-':
            window['-LOG-'].update("\n"+values[event])
        elif event == '-TASKFINISH-':
            window['GO'].update("START")
            reduce_ser = None

        elif event == "GO":
            if reduce_ser!=None:
                reduce_ser.stop()
                window['GO'].update("START")
            else:
                error = ""

                if values['-OPTION_PERCENTAGE-']:
                    percent = True
                else:
                    percent = False

                text = values['number']
                if text=="":
                    error = "[Number is empty]"
                else:
                    try:
                        value = int(text)
                        if percent and (value>100 or value<10):
                            error = "[error with percentage, should be between 10 and 100]"
                        else:
                            if not percent and value<50:
                                error = "[error with frame number, should be superior to 50]"                    
                    except:
                        error = "[Not an integer]"
                if values['-FOLDER-']=="":
                    error += " [Folder is empty]"
                subdir = values['-SUBDIR-']
                delete = values['-DELETE-']
                suffix = values['-SUFFIX-']

                if error!="":
                    window['-ERROR-'].update(error)
                else:
                    window['-ERROR-'].update("")
                    window['GO'].update("STOP")
                    reduce_ser = ReduceSer(values['-FOLDER-'],suffix, subdir, value, percent, delete,callback.callback,sg.cprint)
                    reduce_ser.start()

                
                


    window.close()


if __name__ == "__main__":
    run()