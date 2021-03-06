from Tkinter import *
from ttk import Progressbar
import Tkinter, Tkconstants, tkFileDialog
import numpy as np
from lib import GEM_COM_classes as COM_class
import binascii
import communication_error_GUI as error_GUI
from multiprocessing import Process, Pipe
import acq_GUI as acq_GUI
from lib import GEM_ANALYSIS_classes as AN_CLASS, GEM_CONF_classes as GEM_CONF
import sys
import array

OS = sys.platform
if OS == 'win32':
    sep = '\\'
elif OS == 'linux2':
    sep = '/'
else:
    print("ERROR: OS {} non compatible".format(OS))
    sys.exit()


# TODO: bugs:
# Add completition bars for TD scan
# Acquire Errors since last reset.
# TODO: LV settings
class menu():
    def __init__(self):
        self.GEM_to_config = np.zeros((20))
        self.configuring_gemroc = 0
        # main window
        self.main_window = Tk()
        self.icon_on = PhotoImage(file="." + sep + 'icons' + sep + 'on.gif')
        self.icon_off = PhotoImage(file="." + sep + 'icons' + sep + 'off.gif')
        self.icon_bad = PhotoImage(file="." + sep + 'icons' + sep + 'bad.gif')
        self.main_window.title("GEMROC configurer")
        self.handler_list = []
        self.GEMROC_reading_dict = {}
        self.showing_GEMROC = StringVar(self.main_window)
        self.entry_text = StringVar(self.main_window)

        self.showing_TIGER = StringVar(self.main_window)
        self.showing_CHANNEL = StringVar(self.main_window)
        self.configure_MODE = StringVar(self.main_window)

        self.all_channels = StringVar(self.main_window)
        self.all_TIGERs = StringVar(self.main_window)
        self.all_GEMROCs = StringVar(self.main_window)
        self.rate=IntVar(self.main_window)
        # fields_options=["DAQ configuration", "LV configuration", "Global Tiger configuration", "Channel Tiger configuration"]
        fields_options = ["DAQ configuration", "Global Tiger configuration", "Channel Tiger configuration"]
        Label(self.main_window, text='Configuration', font=("Courier", 25)).pack()
        self.conf_frame = Frame(self.main_window)
        self.conf_frame.pack()
        self.first_row_frame = Frame(self.conf_frame)
        self.first_row_frame.grid(row=0, column=0, sticky=NW, pady=4)
        self.select_MODE = OptionMenu(self.first_row_frame, self.configure_MODE, *fields_options)
        self.select_MODE.grid(row=0, column=0, sticky=NW, pady=4)
        Label(self.first_row_frame, text="Errors").grid(row=0, column=1, sticky=W, padx=10)
        self.ERROR_LED = Label(self.first_row_frame, image=self.icon_off)
        self.ERROR_LED.grid(row=0, column=2, sticky=W, padx=1)
        self.second_row_frame = Frame(self.conf_frame)
        self.second_row_frame.grid(row=1, column=0, sticky=NW, pady=4)
        self.label_array = []
        self.field_array = []
        self.input_array = []
        self.configure_MODE.trace('w', self.update_menu)
        self.dict_pram_list = []
        self.third_row_frame = Frame(self.conf_frame)

        ##Select window
        self.select_window = Toplevel(self.main_window)

        Label(self.select_window, text='GEMROC to configure', font=("Courier", 25)).pack()
        self.grid_frame = Frame(self.select_window)
        self.grid_frame.pack()
        Button(self.grid_frame, text='ROC 00', command=lambda: self.toggle(0)).grid(row=0, column=0, sticky=NW, pady=15)
        Button(self.grid_frame, text='ROC 01', command=lambda: self.toggle(1)).grid(row=0, column=2, sticky=NW, pady=15)
        Button(self.grid_frame, text='ROC 02', command=lambda: self.toggle(2)).grid(row=0, column=4, sticky=NW, pady=15)
        Button(self.grid_frame, text='ROC 03', command=lambda: self.toggle(3)).grid(row=0, column=6, sticky=W, pady=15)
        Button(self.grid_frame, text='ROC 04', command=lambda: self.toggle(4)).grid(row=0, column=8, sticky=W, pady=15)
        Button(self.grid_frame, text='ROC 05', command=lambda: self.toggle(5)).grid(row=0, column=10, sticky=W, pady=15)
        Button(self.grid_frame, text='ROC 06', command=lambda: self.toggle(6)).grid(row=0, column=12, sticky=NW, pady=15)
        Button(self.grid_frame, text='ROC 07', command=lambda: self.toggle(7)).grid(row=0, column=14, sticky=NW, pady=15)
        Button(self.grid_frame, text='ROC 08', command=lambda: self.toggle(8)).grid(row=0, column=16, sticky=NW, pady=15)
        Button(self.grid_frame, text='ROC 09', command=lambda: self.toggle(9)).grid(row=0, column=18, sticky=NW, pady=15)
        Button(self.grid_frame, text='ROC 10', command=lambda: self.toggle(10)).grid(row=1, column=0, sticky=NW, pady=15)
        Button(self.grid_frame, text='ROC 11', command=lambda: self.toggle(11)).grid(row=1, column=2, sticky=NW, pady=15)
        Button(self.grid_frame, text='ROC 12', command=lambda: self.toggle(12)).grid(row=1, column=4, sticky=W, pady=15)
        Button(self.grid_frame, text='ROC 13', command=lambda: self.toggle(13)).grid(row=1, column=6, sticky=W, pady=15)
        Button(self.grid_frame, text='ROC 14', command=lambda: self.toggle(14)).grid(row=1, column=8, sticky=W, pady=15)
        Button(self.grid_frame, text='ROC 15', command=lambda: self.toggle(15)).grid(row=1, column=10, sticky=NW, pady=15)
        Button(self.grid_frame, text='ROC 16', command=lambda: self.toggle(16)).grid(row=1, column=12, sticky=NW, pady=15)
        Button(self.grid_frame, text='ROC 17', command=lambda: self.toggle(17)).grid(row=1, column=14, sticky=NW, pady=15)
        Button(self.grid_frame, text='ROC 18', command=lambda: self.toggle(18)).grid(row=1, column=16, sticky=NW, pady=15)
        Button(self.grid_frame, text='ROC 19', command=lambda: self.toggle(19)).grid(row=1, column=18, sticky=NW, pady=15)
        self.error_frame = Frame(self.select_window)
        self.error_frame.pack()
        Label(self.error_frame, text='Message ').grid(row=0, column=1, sticky=NW, pady=4)
        self.Launch_error_check = Label(self.error_frame, text='-', background='white')
        self.Launch_error_check.grid(row=0, column=2, sticky=NW, pady=4)
        Tante_frame = Frame(self.select_window)
        Tante_frame.pack()
        Button(Tante_frame, text="Sync Reset to all", command=self.Synch_reset).pack(side=LEFT)
        Button(Tante_frame, text="Set ext clock to all", command=lambda: self.change_clock_mode(1, 1)).pack(side=LEFT)
        Button(Tante_frame, text="Set int clock to all", command=lambda: self.change_clock_mode(1, 0)).pack(side=LEFT)
        Button(Tante_frame, text="Set pause mode to all", command=lambda: self.set_pause_mode(True, 1)).pack(side=LEFT)
        Button(Tante_frame, text="Disable pause mode to all", command=lambda: self.set_pause_mode(True, 0)).pack(side=LEFT)
        Button(Tante_frame, text="Set trigger-less mode to all", command=lambda: self.change_acquisition_mode(True, 1)).pack(side=LEFT)
        Button(Tante_frame, text="Set trigger-matched to all", command=lambda: self.change_acquisition_mode(True, 0)).pack(side=LEFT)
        Tantissime_frame = Frame(self.select_window)
        Tantissime_frame.pack()
        Button(Tantissime_frame, text="Configure all chips with default settings", command=self.load_default_config).pack(side=LEFT)
        Button(Tantissime_frame, text="Open communication error interface", command=self.open_communicaton_GUI).pack(side=LEFT)

        cornice=Frame(self.select_window)
        cornice.pack()
        Button(cornice, text="THR scan on all GEMROCs", command=lambda: self.thr_Scan(-1, -1)).pack(side=LEFT)
        Label(cornice, text="Rate").pack(side=LEFT)
        Entry(cornice,textvar=self.rate,width=5 ).pack(side=LEFT)
        Button(cornice, text="Set threshold aiming to a certain rate", command=lambda: self.auto_tune(-1, -1,15)).pack(side=LEFT)
        Button(cornice, text="Load thresholds to all", command=lambda: self.load_thr(True, source="scan")).pack(side=LEFT)

        Button(cornice, text="Load auto-thr to all", command=lambda: self.load_thr(True, source="auto")).pack(side=LEFT)

        Frame(self.select_window, height=20).pack()

        TROPPE_frame = LabelFrame(self.select_window, padx=5, pady=5)
        TROPPE_frame.pack(side=LEFT)
        Button(TROPPE_frame, text="FEB power ON", command=self.power_on_FEBS, activeforeground="green").pack(side=LEFT)

        Button(TROPPE_frame, text="FEB power OFF", command=self.power_off_FEBS, activeforeground="red").pack(side=LEFT)
        TROPPi_frame = LabelFrame(self.select_window, padx=5, pady=5)
        TROPPi_frame.pack(side=RIGHT)
        Button(TROPPi_frame, text="Run controller", command=self.launch_controller, activeforeground="blue").pack(side=RIGHT)

        self.LED = []
        for i in range(0, len(self.GEM_to_config)):
            if i < 10:
                riga = 0
            else:
                riga = 1

            colonna = ((i) % 10) * 2 + 1
            self.LED.append(Label(self.grid_frame, image=self.icon_off))
            self.LED[i].grid(row=riga, column=colonna)

    def launch_controller(self):
        self.acq = acq_GUI.menu(False, self.main_window, self.GEMROC_reading_dict)

    def open_communicaton_GUI(self):
        #print self.GEMROC_reading_dict
        self.conf_wind = error_GUI.menu(self.main_window, self.GEMROC_reading_dict)

    def runna(self):
        mainloop()
        # while True:
        #     self.main_window.update_idletasks()
        #     self.main_window.update()

    def toggle(self, i):
        if self.GEM_to_config[i] == 0:
            self.GEM_to_config[i] = 1
        else:
            self.GEM_to_config[i] = 0
        self.convert0(i)

    def convert0(self, i):
        if self.GEM_to_config[i] == 1:
            try:
                self.handler_list.append(GEMROC_HANDLER(i))
                self.LED[i]["image"] = self.icon_on
            except  Exception as error:
                self.Launch_error_check['text'] = "GEMROC {}: {}".format(i, error)
                self.LED[i]["image"] = self.icon_bad
            else:
                self.Launch_error_check['text'] = "Communication with GEMROC {} enstablished".format(i)


        else:
            self.LED[i]["image"] = self.icon_off
            for j in range(0, len(self.handler_list)):
                if self.handler_list[j].GEMROC_ID == i:
                    self.handler_list[j].__del__()
                    del self.handler_list[j]
                    self.Launch_error_check['text'] = "Communication with GEMROC {} closed".format(i)
                    break
        self.update_menu(1, 2, 3)

    def update_menu(self, a, b, c):
        self.second_row_frame.destroy()
        self.second_row_frame = Frame(self.conf_frame)
        self.second_row_frame.grid(row=1, column=0, sticky=NW, pady=4)
        self.GEMROC_reading_dict = {}
        for i in range(0, len(self.handler_list)):
            ID = self.handler_list[i].GEMROC_ID
            self.GEMROC_reading_dict["GEMROC {}".format(ID)] = self.handler_list[i]
        Label(self.second_row_frame, text='GEMROC   ').grid(row=0, column=0, sticky=NW, pady=4)
        # print self.GEMROC_reading_dict.keys()
        self.select_GEMROC = OptionMenu(self.second_row_frame, self.showing_GEMROC, *self.GEMROC_reading_dict.keys())
        self.select_GEMROC.grid(row=1, column=0, sticky=NW, pady=4)
        fields_options = ["DAQ configuration", "LV configuration", "Global Tiger configuration", "Channel Tiger configuration"]

        if self.configure_MODE.get() == "DAQ configuration":
            self.Go = Button(self.second_row_frame, text='Go', command=self.DAQ_configurator)
            self.Go.grid(row=1, column=5, sticky=NW, pady=4)


        elif self.configure_MODE.get() == "LV configuration":
            self.Go = Button(self.second_row_frame, text='Go', command=self.update_menu)
            self.Go.grid(row=1, column=5, sticky=NW, pady=4)


        elif self.configure_MODE.get() == "Global Tiger configuration":
            Label(self.second_row_frame, text='TIGER   ').grid(row=0, column=1, sticky=NW, pady=4)
            self.select_TIGER = OptionMenu(self.second_row_frame, self.showing_TIGER, *range(8))
            self.select_TIGER.grid(row=1, column=1, sticky=NW, pady=4)
            self.Go = Button(self.second_row_frame, text='Go', command=self.TIGER_GLOBAL_configurator)
            self.Go.grid(row=1, column=5, sticky=NW, pady=4)


        elif self.configure_MODE.get() == "Channel Tiger configuration":
            Label(self.second_row_frame, text='TIGER   ').grid(row=0, column=1, sticky=W, pady=4)
            self.select_TIGER = OptionMenu(self.second_row_frame, self.showing_TIGER, *range(8))
            self.select_TIGER.grid(row=1, column=1, sticky=W, pady=4)
            Label(self.second_row_frame, text='Channel   ').grid(row=0, column=2, sticky=W, pady=4)
            self.Channel_IN = Entry(self.second_row_frame, width=4, textvariable=self.entry_text)
            self.entry_text.trace("w", lambda *args: character_limit(self.entry_text))
            self.Channel_IN.grid(row=1, column=2, sticky=W, pady=4)
            self.Go = Button(self.second_row_frame, text='Go', command=self.TIGER_CHANNEL_configurator)
            self.Go.grid(row=1, column=5, sticky=NW, pady=4)

    def power_on_FEBS(self):
        for number, GEMROC in self.GEMROC_reading_dict.items():
            GEMROC.GEM_COM.FEBPwrEnPattern_set(255)

    def power_off_FEBS(self):
        for number, GEMROC in self.GEMROC_reading_dict.items():
            GEMROC.GEM_COM.FEBPwrEnPattern_set(0)
    def auto(self,GEMROC_num, TIGER_nume,rate):
        print rate
    def thr_Scan(self, GEMROC_num, TIGER_num):  # if GEMROC num=-1--> To all GEMROC, if TIGER_num=-1 --> To all TIGERs
        self.bar_win = Toplevel(self.main_window)
        self.bar_win.focus_set()  # set focus on the ProgressWindow
        self.bar_win.grab_set()
        progress_bars = []
        progress_list = []
        dict = {}

        Label(self.bar_win, text="Threshold Scan completition").pack()
        if GEMROC_num == -1:
            dict = self.GEMROC_reading_dict.copy()
        else:
            dict["{}".format(GEMROC_num)] = self.GEMROC_reading_dict[GEMROC_num]
        i = 0
        for number, GEMROC_number in dict.items():
            Label(self.bar_win, text='{}'.format(number)).pack()
            progress_list.append(IntVar())
            if TIGER_num == -1:
                maxim = 32768
            else:
                maxim = 4096
            progress_bars.append(Progressbar(self.bar_win, maximum=maxim, orient=HORIZONTAL, variable=progress_list[i], length=200, mode='determinate'))
            progress_bars[i].pack()

            i += 1
        process_list = []
        pipe_list = []
        i = 0
        for number, GEMROC_num in dict.items():
            pipe_in, pipe_out = Pipe()
            p = Process(target=self.THR_scan_process, args=(number, TIGER_num, pipe_out))
            # pipe_in.send(progress_bars[i])
            process_list.append(p)
            pipe_list.append(pipe_in)
            p.start()
            i += 1
        while True:
            alive_list = []
            for process in process_list:
                alive_list.append(process.is_alive())
            if all(v == 0 for v in alive_list):
                break
            else:
                for progress, pipe in zip(progress_list, pipe_list):
                    try:
                        progress.set(pipe.recv())
                    except:
                        Exception("Can't acquire status")
                        #print ("Can't acquire status")

                    self.bar_win.update()
                    # print progress.get()

        for process in process_list:
            if process.is_alive():
                process.join()
        self.bar_win.destroy()

        # else:
        #     GEMROC = self.GEMROC_reading_dict["GEMROC {}".format(GEMROC_num)]
        #     GEM_COM = GEMROC.GEM_COM
        #     c_inst = GEMROC.c_inst
        #     g_inst = GEMROC.g_inst
        #     test_r = (AN_CLASS.analisys_conf(GEM_COM, c_inst, g_inst))

    def THR_scan_process(self, number, TIGER, pipe_out):
        print number
        print TIGER
        GEMROC = self.GEMROC_reading_dict[number]
        GEM_COM = GEMROC.GEM_COM
        c_inst = GEMROC.c_inst
        g_inst = GEMROC.g_inst
        test_c = AN_CLASS.analisys_conf(GEM_COM, c_inst, g_inst)
        test_r = AN_CLASS.analisys_read(GEM_COM, c_inst)
        test_c.thr_preconf()
        if TIGER == -1:
            first = 0
            last = 8
        else:
            first = TIGER
            last = TIGER + 1
        GEMROC_ID = GEM_COM.GEMROC_ID
        test_r.thr_scan_matrix = test_c.thr_conf_using_GEMROC_COUNTERS_progress_bar(test_r, first, last, pipe_out, False)

        test_r.make_rate()
        test_r.normalize_rate(first, last)
        test_r.save_scan_on_file()
        test_r.colorPlot(GEM_COM.Tscan_folder + sep + "GEMROC{}".format(GEMROC_ID) + sep + "GEMROC {}".format(GEMROC_ID) + "rate", first, last, True)
        test_r.colorPlot(GEM_COM.Tscan_folder + sep + "GEMROC{}".format(GEMROC_ID) + sep + "GEMROC {}".format(GEMROC_ID) + "conteggi", first, last)

        # test_r.normalize_rate( first,int(input_array[2]))
        test_r.global_sfit(first, last)
        print "GEMROC {} done".format(GEMROC_ID)

    def auto_tune(self, GEMROC_num, TIGER_num,iter):  # if GEMROC num=-1--> To all GEMROC, if TIGER_num=-1 --> To all TIGERs
        self.bar_win = Toplevel(self.main_window)
        self.bar_win.focus_set()  # set focus on the ProgressWindow
        self.bar_win.grab_set()
        progress_bars = []
        progress_list = []
        dict = {}

        Label(self.bar_win, text="Auto tune completition").pack()
        if GEMROC_num == -1:
            dict = self.GEMROC_reading_dict.copy()
        else:
            dict["{}".format(GEMROC_num)] = self.GEMROC_reading_dict[GEMROC_num]
        i = 0
        for number, GEMROC_number in dict.items():
            Label(self.bar_win, text='{}'.format(number)).pack()
            progress_list.append(IntVar())
            if TIGER_num == -1:
                maxim = 8*iter
            else:
                maxim = iter
            progress_bars.append(Progressbar(self.bar_win, maximum=maxim, orient=HORIZONTAL, variable=progress_list[i], length=200, mode='determinate'))
            progress_bars[i].pack()

            i += 1
        process_list = []
        pipe_list = []
        i = 0
        for number, GEMROC_num in dict.items():
            pipe_in, pipe_out = Pipe()
            p = Process(target=self.auto_tune_process, args=(number, TIGER_num, pipe_out,iter))
            # pipe_in.send(progress_bars[i])
            process_list.append(p)
            pipe_list.append(pipe_in)
            p.start()
            i += 1
        while True:
            alive_list = []
            for process in process_list:
                alive_list.append(process.is_alive())
            if all(v == 0 for v in alive_list):
                break
            else:
                for progress, pipe in zip(progress_list, pipe_list):
                    try:
                        progress.set(pipe.recv())
                    except:
                        Exception("Can't acquire status")
                        #print ("Can't acquire status")

                    self.bar_win.update()
                    # print progress.get()

        for process in process_list:
            if process.is_alive():
                process.join()
        self.bar_win.destroy()

        # else:
        #     GEMROC = self.GEMROC_reading_dict["GEMROC {}".format(GEMROC_num)]
        #     GEM_COM = GEMROC.GEM_COM
        #     c_inst = GEMROC.c_inst
        #     g_inst = GEMROC.g_inst
        #     test_r = (AN_CLASS.analisys_conf(GEM_COM, c_inst, g_inst))

    def auto_tune_process(self, number, TIGER, pipe_out,iter):
        print number
        print TIGER
        GEMROC = self.GEMROC_reading_dict[number]
        GEM_COM = GEMROC.GEM_COM
        c_inst = GEMROC.c_inst
        g_inst = GEMROC.g_inst
        rate=int(self.rate.get())
        if TIGER != -1:
            test_r = AN_CLASS.analisys_read(GEM_COM, c_inst)

            auto_tune_C = AN_CLASS.analisys_conf(GEM_COM, c_inst, g_inst)
            GEM_COM.Load_VTH_fromfile(c_inst, TIGER, 2, 0)
            print "\nVth Loaded on TIGER {}".format(TIGER)
            auto_tune_C.fill_VTHR_matrix(3, 0, TIGER)

            auto_tune_C.thr_autotune_wth_counter_progress(TIGER, rate, test_r,pipe_out, iter, 0.03)
            #auto_tune_C.thr_autotune_wth_counter_progress(TIGER, rate, test_r,pipe_out, 2, 1)

            auto_tune_C.__del__()

            test_r.__del__()

        else:
            for T in range(0, 8):
                test_r = AN_CLASS.analisys_read(GEM_COM, c_inst)

                auto_tune_C = AN_CLASS.analisys_conf(GEM_COM, c_inst, g_inst)
                GEM_COM.Load_VTH_fromfile(c_inst, T, 2, 0)
                print "\nVth Loaded on TIGER {}".format(T)
                auto_tune_C.fill_VTHR_matrix(3, 0, T)

                auto_tune_C.thr_autotune_wth_counter_progress(T, rate, test_r, pipe_out,iter, 0.03)
                #auto_tune_C.thr_autotune_wth_counter_progress(T, rate, test_r, pipe_out,2, 1)

                auto_tune_C.__del__()

                test_r.__del__()

        GEMROC_ID = GEM_COM.GEMROC_ID
               # test_r.normalize_rate( first,int(input_array[2]))
        print "GEMROC {} done".format(GEMROC_ID)



    def TIGER_CHANNEL_configurator(self):
        self.dict_pram_list = self.GEMROC_reading_dict['{}'.format(self.showing_GEMROC.get())].c_inst.Channel_cfg_list[int(self.showing_TIGER.get())][int(self.Channel_IN.get())].keys()
        self.third_row_frame.destroy()
        self.third_row_frame = Frame(self.conf_frame)
        self.third_row_frame.grid(row=2, column=0, sticky=NW, pady=4)
        single_use_frame = Frame(self.third_row_frame)
        single_use_frame.grid(row=1, column=0, sticky=W, pady=2)
        tasti = Frame(self.third_row_frame)
        tasti.grid(row=0, column=0, sticky=W, pady=2)
        Button(tasti, text='Read configuration', command=self.read_TIGER_channel).grid(row=0, column=1, sticky=W, pady=2)
        Button(tasti, text='Write configuration', command=self.write_CHANNEL_Handling).grid(row=0, column=2, sticky=W, pady=2)
        OptionMenu(tasti, self.all_channels, *["All Channels", "-"]).grid(row=0, column=3, sticky=W, pady=2)
        OptionMenu(tasti, self.all_TIGERs, *["All TIGERs", "-"]).grid(row=0, column=4, sticky=W, pady=2)
        OptionMenu(tasti, self.all_GEMROCs, *["All GEMROCs", "-"]).grid(row=0, column=5, sticky=W, pady=2)
        self.label_array = []
        self.field_array = []
        self.input_array = {}
        with open("lib" + sep + "keys" + sep + "channel_conf_file_keys", 'r') as f:
            i = 0
            j = 0
            lenght = len(f.readlines())
            # print lenght
            f.seek(0)
            Label(single_use_frame, text="Read").grid(row=1, column=1, sticky=W, pady=0, padx=2)
            Label(single_use_frame, text="To load").grid(row=1, column=2, sticky=W, pady=0, padx=2)
            Label(single_use_frame, text="Read").grid(row=1, column=4, sticky=W, pady=0, padx=2)
            Label(single_use_frame, text="To load").grid(row=1, column=5, sticky=W, pady=0, padx=2)

            for line in f.readlines():
                line = line.rstrip('\n')
                self.field_array.append(Label(single_use_frame, text='-'))
                if line in self.dict_pram_list:
                    self.input_array[line] = (Entry(single_use_frame, width=3))
                self.label_array.append(Label(single_use_frame, text=line))

                if i < lenght / 2:
                    self.label_array[i].grid(row=i + 2, column=0, sticky=W, pady=0)
                    # print line
                    # print dict_pram_list
                    if str(line) in self.dict_pram_list:
                        self.input_array[line].grid(row=i + 2, column=2, sticky=W, pady=0)
                        j += 1
                    self.field_array[i].grid(row=i + 2, column=1, sticky=W, pady=0)
                else:
                    self.label_array[i].grid(row=i + 2 - lenght / 2, column=3, sticky=W, pady=0)
                    if line in self.dict_pram_list:
                        self.input_array[line].grid(row=i + 2 - lenght / 2, column=5, sticky=W, pady=0)
                        j += 1
                    self.field_array[i].grid(row=i + 2 - lenght / 2, column=4, sticky=W, pady=0)

                i += 1
            thr_target = StringVar(self.third_row_frame)
            thr_target.set("This TIGER")
            saveframe = Frame(self.third_row_frame)
            saveframe.grid(row=4, column=0, sticky=W, pady=2)
            Button(saveframe, text="Save", command=self.SAVE).pack(side=LEFT)
            Button(saveframe, text="Load", command=self.LOAD).pack(side=LEFT)
            self.LOAD_ON = Button(saveframe, text="Load on TIGERs (loaded file)", command=self.LOAD_on_TIGER, state='disable')
            self.LOAD_ON.pack(side=LEFT)
            thr_frame = Frame(self.third_row_frame)
            thr_frame.grid(row=3, column=0, sticky=W, pady=2)
            Label(thr_frame, text="Sigma").pack(side=LEFT)
            self.thr_sigma = Entry(thr_frame, width=2)
            self.thr_sigma.pack(side=LEFT)
            OptionMenu(thr_frame, thr_target, *["This TIGER", "All TIGERs", "All TIGERs in all GEMROCs"]).pack(side=LEFT)
            Button(thr_frame, text="Load scan threshold", command=lambda: self.load_thr_Handling(thr_target, "scan")).pack(side=LEFT)
            Button(thr_frame, text="Load auto threshold", command=lambda: self.load_thr_Handling(thr_target, "auto")).pack(side=LEFT)
            Button(thr_frame, text="Launch THR scan on this TIGER", command=lambda: self.thr_Scan(self.showing_GEMROC.get(), int(self.showing_TIGER.get()))).pack(side=LEFT)

    def TIGER_GLOBAL_configurator(self):
        self.third_row_frame.destroy()
        self.third_row_frame = Frame(self.conf_frame)
        self.third_row_frame.grid(row=2, column=0, sticky=NW, pady=4)
        single_use_frame = Frame(self.third_row_frame)
        single_use_frame.grid(row=1, column=0, sticky=W, pady=2)
        tasti = Frame(self.third_row_frame)
        tasti.grid(row=0, column=0, sticky=W, pady=2)
        Button(tasti, text='Read configuration', command=self.read_TIGER_global).grid(row=0, column=1, sticky=W, pady=2)
        Button(tasti, text='Write configuration', command=self.write_TIGER_GLOBAL).grid(row=0, column=2, sticky=W, pady=2)
        Button(tasti, text='Write configuration to all TIGERs on this GEMROC', command=self.write_TIGER_GLOBAL_allGEM).grid(row=0, column=3, sticky=W, pady=2)
        Button(tasti, text='Write configuration to all TIGERs', command=self.write_TIGER_GLOBAL_allsystem).grid(row=0, column=4, sticky=W, pady=2)
        self.label_array = []
        self.field_array = []
        self.input_array = []
        with open("lib" + sep + "keys" + sep + "global_conf_file_keys", 'r') as f:
            i = 0
            lenght = len(f.readlines())
            # print lenght
            f.seek(0)
            Label(single_use_frame, text="Read").grid(row=1, column=1, sticky=W, pady=0)
            Label(single_use_frame, text="To load").grid(row=1, column=2, sticky=W, pady=0)
            Label(single_use_frame, text="Read").grid(row=1, column=4, sticky=W, pady=0)
            Label(single_use_frame, text="To load").grid(row=1, column=5, sticky=W, pady=0)

            for line in f.readlines():
                self.field_array.append(Label(single_use_frame, text='-'))
                self.input_array.append(Entry(single_use_frame, width=3))
                self.label_array.append(Label(single_use_frame, text=line))

                if i < lenght / 2:
                    self.label_array[i].grid(row=i + 2, column=0, sticky=W, pady=0)
                    self.input_array[i].grid(row=i + 2, column=2, sticky=W, pady=0)
                    self.field_array[i].grid(row=i + 2, column=1, sticky=W, pady=0)
                else:
                    self.label_array[i].grid(row=i + 2 - lenght / 2, column=3, sticky=W, pady=0)
                    self.input_array[i].grid(row=i + 2 - lenght / 2, column=5, sticky=W, pady=0)
                    self.field_array[i].grid(row=i + 2 - lenght / 2, column=4, sticky=W, pady=0)

                i += 1
        saveframe = Frame(self.third_row_frame)
        saveframe.grid(row=4, column=0, sticky=W, pady=2)
        Button(saveframe, text="Save", command=self.SAVE).pack(side=LEFT)
        Button(saveframe, text="Load", command=self.LOAD).pack(side=LEFT)

    def SAVE(self):
        if self.configure_MODE.get() == "Global Tiger configuration":
            File_name = tkFileDialog.asksaveasfilename(initialdir="." + sep + "conf" + sep + "saves", title="Select file name", filetypes=(("Global configuration saves", "*.gs"), ("all files", "*.*")))
            GEM_NAME = str(self.showing_GEMROC.get())
            self.GEMROC_reading_dict[GEM_NAME].g_inst.save_glob_conf(File_name)

        if self.configure_MODE.get() == "Channel Tiger configuration":
            File_name = tkFileDialog.asksaveasfilename(initialdir="." + sep + "conf" + sep + "saves", title="Select file name", filetypes=(("Channels configuration saves", "*.cs"), ("all files", "*.*")))
            GEM_NAME = str(self.showing_GEMROC.get())
            self.GEMROC_reading_dict[GEM_NAME].c_inst.save_ch_conf(File_name)

    def LOAD(self):
        if self.configure_MODE.get() == "Global Tiger configuration":
            GEM_NAME = str(self.showing_GEMROC.get())
            File_name = tkFileDialog.askopenfilename(initialdir="." + sep + "conf" + sep + "saves", title="Select file", filetypes=(("Global configuration saves", "*.gs"), ("all files", "*.*")))
            self.GEMROC_reading_dict[GEM_NAME].g_inst.load_glob_conf(File_name)

        if self.configure_MODE.get() == "Channel Tiger configuration":
            GEM_NAME = str(self.showing_GEMROC.get())
            File_name = tkFileDialog.askopenfilename(initialdir="." + sep + "conf" + sep + "saves", title="Select file", filetypes=(("Channels configuration saves", "*.cs"), ("all files", "*.*")))
            self.GEMROC_reading_dict[GEM_NAME].c_inst.load_ch_conf(File_name)
        self.LOAD_ON.config(state='normal')

    def LOAD_on_TIGER(self):
        GEMROC = self.showing_GEMROC.get()
        for T in range(0, 8):
            self.write_CHANNEL(self.GEMROC_reading_dict[GEMROC], T, 64, False)

    def DAQ_configurator(self):
        self.third_row_frame.destroy()
        self.third_row_frame = Frame(self.conf_frame)
        self.third_row_frame.grid(row=2, column=0, sticky=NW, pady=4)
        single_use_frame = Frame(self.third_row_frame)
        single_use_frame.grid(row=0, column=0, sticky=W, pady=2)
        Button(single_use_frame, text='Read configuration', command=self.read_DAQ_CR).grid(row=0, column=1, sticky=W, pady=2)
        self.field_array = []
        self.input_array = []
        self.label_array = []
        with open("lib" + sep + "keys" + sep + "DAQ_cr_keys", 'r') as f:
            i = 0

            for line in f.readlines():
                self.label_array.append(Label(single_use_frame, text=line.rstrip('\n')))
                self.label_array[i].grid(row=i + 1, column=0, sticky=W, pady=0)
                self.field_array.append(Label(single_use_frame, text='-'))
                self.field_array[i].grid(row=i + 1, column=1, sticky=W, pady=0)
                # self.input_array.append(Entry(single_use_frame,))
                # self.input_array[i].grid(row=i, column=2, sticky=W, pady=2)
                i += 1
        another_frame = Frame(self.third_row_frame)
        another_frame.grid(row=0, column=1, sticky=W, pady=2)
        Label(another_frame, text="Change configuration", font=("Courier", 20)).grid(row=0, column=0, columnspan=8, sticky=S, pady=5)
        # modebut=Button(another_frame, text="Trigger matched",command= lambda : self.switch_mode(modebut))
        # modebut.grid(row=1, column=1, sticky=W, pady=2)

        Label(another_frame, text="TCAM_Enable_pattern").grid(row=2, column=0, sticky=S, pady=0)
        Label(another_frame, text="Periodic_FEB_TP_Enable_pattern").grid(row=3, column=0, sticky=S, pady=0)
        Label(another_frame, text="TP_repeat_burst").grid(row=4, column=0, sticky=S, pady=0)
        Label(another_frame, text="TP_Num_in_burst").grid(row=5, column=0, sticky=S, pady=0)
        Label(another_frame, text="TL_nTM_ACQ_choice").grid(row=6, column=0, sticky=S, pady=0)
        # Label(another_frame,text="Periodic_L1_Enable_BIT").grid(row=7, column=0,sticky=S, pady=0) #E' lo stesso di periodic FEB_TP_Enable pattern
        Label(another_frame, text="Enab_Auto_L1_from_TP_bit_param").grid(row=8, column=0, sticky=S, pady=0)
        Label(another_frame, text="Enable_DAQPause_Until_First_Trigger").grid(row=9, column=0, sticky=S, pady=0)
        # Label(another_frame,text="DAQPause_Set").grid(row=10, column=0,sticky=S, pady=0)
        # Label(another_frame,text="Tpulse_gen_w_ext_trigger_enable").grid(row=11, column=0,sticky=S, pady=0)
        Label(another_frame, text="EXT_nINT_B3clk").grid(row=12, column=0, sticky=S, pady=0)

        self.IN1 = Entry(another_frame)
        self.IN1.grid(row=2, column=1, sticky=S, pady=0)
        self.IN2 = Entry(another_frame)
        self.IN2.grid(row=3, column=1, sticky=S, pady=0)
        self.IN3 = Entry(another_frame)
        self.IN3.grid(row=4, column=1, sticky=S, pady=0)
        self.IN4 = Entry(another_frame)
        self.IN4.grid(row=5, column=1, sticky=S, pady=0)
        self.IN5 = Entry(another_frame)
        self.IN5.grid(row=6, column=1, sticky=S, pady=0)
        # self.IN6=Entry(another_frame)
        # self.IN6.grid(row=7, column=1,sticky=S, pady=0)
        self.IN7 = Entry(another_frame)
        self.IN7.grid(row=8, column=1, sticky=S, pady=0)
        self.IN8 = Entry(another_frame)
        self.IN8.grid(row=9, column=1, sticky=S, pady=0)
        # self.IN9 = Entry(another_frame)
        # self.IN9.grid(row=10, column=1, sticky=S, pady=0)
        # self.IN10 = Entry(another_frame)
        # self.IN10.grid(row=11, column=1, sticky=S, pady=0)
        self.IN11 = Entry(another_frame)
        self.IN11.grid(row=12, column=1, sticky=S, pady=0)

        Button(another_frame, text='Set', command=self.write_DAQ_CR).grid(row=15, column=15, sticky=W, pady=2)
        Button(another_frame, text='Set on all active GEMROCs', command=lambda: self.write_DAQ_CR(1)).grid(row=15, column=16, sticky=W, pady=2)
        I_love_frames = Frame(self.third_row_frame)
        I_love_frames.grid(row=2, column=1, sticky=W, pady=2)

        Button(I_love_frames, text="Sync Reset this GEMROC", command=lambda: self.Synch_reset(0)).pack(side=LEFT)
        self.Pause_state = Button(I_love_frames, text="GEMROC_paused", command=self.set_pause_mode)
        self.Clock_state = Button(I_love_frames, text="Internal clock", command=self.change_clock_mode)
        self.Acq_state = Button(I_love_frames, text="Trigger matched", command=self.change_acquisition_mode)
        self.check_clock_state()
        self.check_acq_state()
        self.check_pause_state()
        self.Clock_state.pack(side=LEFT)
        self.Pause_state.pack(side=LEFT)
        self.Acq_state.pack(side=LEFT)
        another1=LabelFrame(self.third_row_frame)
        another1.grid(row=1, column=1, sticky=W, pady=2)
        Label(another1, text="Trigger window settings", font=("Courier", 20)).grid(row=0, column=0, columnspan=8, sticky=S, pady=5)


        Label(another1, text="L1_lat_B3clk_param").grid(row=1, column=2, sticky=S, pady=0)
        self.L1_field1=Label(another1, text="---",width=4)
        self.L1_field1.grid(row=1, column=1, sticky=S, pady=0)
        self.L1_entry1=Entry(another1, width=5)
        Label(another1, text="L1_win_upper_edge_offset_Tiger_clk").grid(row=1, column=0, sticky=S, pady=0)

        self.L1_entry1.grid(row=1, column=3, sticky=S, pady=0)

        Label(another1, text="TM_window_in_B3clk_param").grid(row=2, column=2, sticky=S, pady=0)
        self.L1_field2=Label(another1, text="---",width=4)
        self.L1_field2.grid(row=2, column=1, sticky=S, pady=0)
        self.L1_entry2=Entry(another1, width=5)
        Label(another1, text="L1_win_lower_edge_offset").grid(row=2, column=0, sticky=S, pady=0)

        self.L1_entry2.grid(row=2, column=3, sticky=S, pady=0)


    def check_clock_state(self):
        button = self.Clock_state
        for label, field in zip(self.label_array, self.field_array):
            if label.cget('text').split()[0] == "Debug_Fun_Ctl_Lo4bit[0]":
                if field.cget('text') == 1:
                    button['text'] = "External clock"
                    button['state'] = "normal"

                elif field.cget('text') == 0:
                    button['text'] = "Internal clock"
                    button['state'] = "normal"

                else:
                    button['text'] = "----------"
                    button['state'] = "disable"
                break

    def check_acq_state(self):
        button = self.Acq_state
        for label, field in zip(self.label_array, self.field_array):
            if label.cget('text').split()[0] == "TL_nTM_ACQ":
                if field.cget('text') == 1:
                    button['text'] = "Trigger-less"
                    button['state'] = "normal"

                elif field.cget('text') == 0:
                    button['text'] = "Trigger-Matched"
                    button['state'] = "normal"

                else:
                    button['text'] = "----------"
                    button['state'] = "disable"
                break

    def check_pause_state(self):
        button = self.Pause_state
        for label, field in zip(self.label_array, self.field_array):
            if label.cget('text').split()[0] == "Debug_Fun_Ctl_Lo4bit[3]":
                if field.cget('text') == 1:
                    button['text'] = "Pause mode set, running"
                    button['state'] = "normal"
                    for label, field in zip(self.label_array, self.field_array):
                        if label.cget('text').split()[0] == "Debug_Fun_Ctl_Lo4bit[2]" == 0:
                            button['text'] = "Paused"
                            button['state'] = "normal"
                            break



                elif field.cget('text') == 0:
                    button['text'] = "Un-paused"
                    button['state'] = "normal"

                else:
                    button['text'] = "----------"
                    button['state'] = "disable"
                break

    def set_pause_mode(self, to_all=False, value=1):
        if to_all == False:
            GEMROC = self.GEMROC_reading_dict[self.showing_GEMROC.get()]
            if self.Pause_state['text'] == "Paused":
                GEMROC.GEM_COM.DAQ_set_Pause_Mode(0)
            else:
                GEMROC.GEM_COM.DAQ_set_Pause_Mode(1)
                GEMROC.GEM_COM.DAQ_Toggle_Set_Pause_bit()
            self.read_DAQ_CR()
            self.check_pause_state()
        if to_all == True:
            for number, GEMROC in self.GEMROC_reading_dict.items():
                GEMROC.GEM_COM.DAQ_set_Pause_Mode(value)
                if value == 1:
                    GEMROC.GEM_COM.DAQ_Toggle_Set_Pause_bit()

    def change_clock_mode(self, to_all=0, value=0):
        if to_all == 0:
            GEMROC = self.GEMROC_reading_dict[self.showing_GEMROC.get()]

            if self.Clock_state['text'] == "Internal clock":
                GEMROC.GEM_COM.DAQ_set_DAQck_source(1)
            else:
                GEMROC.GEM_COM.DAQ_set_DAQck_source(0)
            self.read_DAQ_CR()
            self.check_clock_state()
        if to_all == 1:
            for number, GEMROC in self.GEMROC_reading_dict.items():
                GEMROC.GEM_COM.DAQ_set_DAQck_source(value)

    def change_acquisition_mode(self, to_all=False, value=1):
        if to_all == 0:
            GEMROC = self.GEMROC_reading_dict[self.showing_GEMROC.get()]

            if self.Acq_state['text'] == "Trigger-less":
                GEMROC.GEM_COM.change_acq_mode(0)
            else:
                GEMROC.GEM_COM.change_acq_mode(1)
            self.read_DAQ_CR()
            self.check_acq_state()
        if to_all == 1:
            for number, GEMROC in self.GEMROC_reading_dict.items():
                GEMROC.GEM_COM.change_acq_mode(value)

    def switch_mode(self, modebut):
        if modebut['text'] == "Trigger matched":
            modebut['text'] = "Trigger less"
        elif modebut['text'] == "Trigger less":
            modebut['text'] = "Trigger matched"

    def write_DAQ_CR(self, to_all=0):  # TODO fix it
        TCAM_Enable_pattern = int(self.IN1.get()) & 0xFF
        Periodic_FEB_TP_Enable_pattern = int(self.IN2.get()) & 0xFF
        TP_repeat_burst = int(self.IN3.get()) & 0x1
        TP_Num_in_burst = int(self.IN4.get()) & 0x1FF
        TL_nTM_ACQ_choice = int(self.IN5.get()) & 0x1
        # Periodic_L1_Enable_bit = int(self.IN6.get()) & 0x1
        Periodic_L1_Enable_bit = int(self.IN2.get()) & 0x1
        Enab_Auto_L1_from_TP_bit_param = int(self.IN7.get()) & 0x1

        DI_Ext_nInt_Clk_option = int(self.IN11.get()) & 0x1
        PauseMode_Enable_Option = int(self.IN8.get()) & 0x1

        # DI_Enab_Auto_L1_from_TP_bit = int(input_array[8], 0) & 0x1  # ACR 2018-11-02 added parameter
        if to_all == 1:

            for i, j in self.GEMROC_reading_dict.items():
                # print "ID:{} Istance {}".format(i,j)
                j.GEM_COM.DAQ_set(TCAM_Enable_pattern, Periodic_FEB_TP_Enable_pattern, TP_repeat_burst, TP_Num_in_burst, TL_nTM_ACQ_choice, Periodic_L1_Enable_bit, Enab_Auto_L1_from_TP_bit_param)
                j.GEM_COM.DAQ_set_Pause_Mode(PauseMode_Enable_Option)
                j.GEM_COM.DAQ_set_DAQck_source(DI_Ext_nInt_Clk_option)

        else:
            GEMROC = self.GEMROC_reading_dict['{}'.format(self.showing_GEMROC.get())]
            GEMROC.GEM_COM.DAQ_set(TCAM_Enable_pattern, Periodic_FEB_TP_Enable_pattern, TP_repeat_burst, TP_Num_in_burst, TL_nTM_ACQ_choice, Periodic_L1_Enable_bit, Enab_Auto_L1_from_TP_bit_param)
            GEMROC.GEM_COM.DAQ_set_Pause_Mode(PauseMode_Enable_Option)
            GEMROC.GEM_COM.DAQ_set_DAQck_source(DI_Ext_nInt_Clk_option)
            GEMROC.GEM_COM.MENU_set_L1_Lat_TM_Win_in_B3Ck_cycles(int(self.L1_entry1.get()),int(self.L1_entry2.get()))
        # print "ok"

    def read_DAQ_CR(self):
        command_reply = self.GEMROC_reading_dict['{}'.format(self.showing_GEMROC.get())].GEM_COM.Read_GEMROC_DAQ_CfgReg()
        # self.GEMROC_reading_dict[self.showing_GEMROC.get()].GEM_COM.display_log_GEMROC_DAQ_CfgReg_readback(command_reply, 1, 1)
        L_array = array.array('I')
        L_array.fromstring(command_reply)
        L_array.byteswap()
        self.L1_field1['text']=((L_array[1] >> 0) & 0xFFFF)
        self.L1_field2['text']=((L_array[2] >> 0) & 0xFFFF)
        self.field_array[0]['text'] = ((L_array[0] >> 16) & 0X1f)
        self.field_array[1]['text'] = ((L_array[0] >> 8) & 0xFF)
        self.field_array[2]['text'] = ((L_array[4] >> 26) & 0xF)
        self.field_array[3]['text'] = ((L_array[1] >> 20) & 0x3FF)
        self.field_array[4]['text'] = ((L_array[1] >> 16) & 0xF)
        # self.field_array[5]['text'] = ((L_array[1] >> 0) & 0xFFFF)
        self.field_array[5]['text'] = ((L_array[2] >> 20) & 0x3FF)
        # self.field_array[7]['text'] = ((L_array[2] >> 16) & 0xF)
        # self.field_array[8]['text'] = ((L_array[3] >> 12) & 0xF)  # acr 2018-11-02
        self.field_array[6]['text'] = ((L_array[3] >> 15) & 0x1)  # acr 2018-11-02
        self.field_array[7]['text'] = ((L_array[3] >> 14) & 0x1)  # acr 2018-11-02
        self.field_array[8]['text'] = ((L_array[3] >> 13) & 0x1)  # acr 2018-11-02
        self.field_array[9]['text'] = ((L_array[3] >> 12) & 0x1)  # acr 2018-11-02
        # self.field_array[13]['text'] = ((L_array[2] >> 0) & 0xFFFF)
        self.field_array[10]['text'] = ((L_array[3] >> 20) & 0x3FF)
        self.field_array[11]['text'] = ((L_array[3] >> 16) & 0xF)
        self.field_array[12]['text'] = ((L_array[3] >> 11) & 0x1)
        self.field_array[13]['text'] = ((L_array[3] >> 10) & 0x1)
        self.field_array[14]['text'] = ((L_array[3] >> 9) & 0x1)
        self.field_array[15]['text'] = ((L_array[3] >> 8) & 0x1)
        self.field_array[16]['text'] = ((L_array[3] >> 0) & 0xFF)
        self.field_array[17]['text'] = ((L_array[4] >> 16) & 0x3FF)
        self.field_array[18] = ((L_array[4] >> 8) & 0x3)
        # self.field_array[23]['text'] = ((L_array[4] >> 6) & 0x1)

        self.IN1.delete(0, END)
        self.IN2.delete(0, END)
        self.IN3.delete(0, END)
        self.IN4.delete(0, END)
        self.IN5.delete(0, END)
        # self.IN6.delete(0,END)
        self.IN7.delete(0, END)
        self.IN8.delete(0, END)

        self.IN11.delete(0, END)

        self.IN1.insert(END, (L_array[3] >> 0) & 0xFF)
        self.IN2.insert(END, (L_array[3] >> 16) & 0xF)
        self.IN3.insert(END, (L_array[3] >> 9) & 0x1)  # TODO verificare!
        self.IN4.insert(END, (L_array[4] >> 16) & 0x3FF)
        self.IN5.insert(END, (L_array[3] >> 11) & 0x1)
        # self.IN6.insert(END,(L_array[3] >> 16) & 0xF)
        self.IN7.insert(END, 0)

        self.IN8.insert(END, ((L_array[3] >> 15) & 0x1))
        # self.IN9.insert(END,((L_array[3] >> 14) & 0x1))
        # self.IN10.insert(END,((L_array[3] >> 13) & 0x1))
        self.IN11.insert(END, ((L_array[3] >> 12) & 0x1))
        self.check_clock_state()
        self.check_pause_state()
        self.check_acq_state()

    def read_TIGER_global(self):
        TIGER_N = int(self.showing_TIGER.get())
        try:
            command_reply = self.GEMROC_reading_dict['{}'.format(self.showing_GEMROC.get())].GEM_COM.ReadTgtGEMROC_TIGER_GCfgReg(self.GEMROC_reading_dict['{}'.format(self.showing_GEMROC.get())].g_inst, TIGER_N)
        except Exception as err:
            print "Can't read configuration - ERROR: {}".format(err)
            self.error_led_update()
            return 0
        L_array = array.array('I')  # L is an array of unsigned long
        L_array.fromstring(command_reply)
        L_array.byteswap()
        for i in range(0, len(self.input_array)):
            self.input_array[i].delete(0, END)
            self.input_array[i].insert(END, self.GEMROC_reading_dict['{}'.format(self.showing_GEMROC.get())].g_inst.Global_cfg_list[int(self.showing_TIGER.get())][self.label_array[i]['text'].rstrip('\n')])

        self.field_array[0]['text'] = ((L_array[1] >> 24) & 0x3)
        self.field_array[1]['text'] = (GEM_CONF.swap_order_N_bits(((L_array[1] >> 16) & 0xF), 4))
        self.field_array[2]['text'] = (GEM_CONF.swap_order_N_bits(((L_array[1] >> 8) & 0x1F), 5))
        self.field_array[3]['text'] = (GEM_CONF.swap_order_N_bits(((L_array[1] >> 0) & 0x3F), 6))
        self.field_array[4]['text'] = (GEM_CONF.swap_order_N_bits(((L_array[2] >> 24) & 0x3F), 6))
        self.field_array[5]['text'] = ((L_array[2] >> 16) & 0x3F)
        self.field_array[6]['text'] = (GEM_CONF.swap_order_N_bits(((L_array[2] >> 8) & 0x1F), 5))
        self.field_array[7]['text'] = (GEM_CONF.swap_order_N_bits(((L_array[2] >> 0) & 0xF), 4))
        self.field_array[8]['text'] = (GEM_CONF.swap_order_N_bits(((L_array[3] >> 24) & 0x1F), 5))
        self.field_array[9]['text'] = (GEM_CONF.swap_order_N_bits(((L_array[3] >> 16) & 0xF), 4))
        self.field_array[10]['text'] = (GEM_CONF.swap_order_N_bits(((L_array[3] >> 8) & 0x3F), 6))
        self.field_array[11]['text'] = ((L_array[3] >> 0) & 0xF)
        self.field_array[12]['text'] = (GEM_CONF.swap_order_N_bits(((L_array[4] >> 24) & 0x3F), 6))
        self.field_array[13]['text'] = ((L_array[4] >> 16) & 0x1F)
        self.field_array[14]['text'] = ((L_array[4] >> 8) & 0x1F)
        self.field_array[15]['text'] = (GEM_CONF.swap_order_N_bits(((L_array[4] >> 0) & 0x3F), 6))
        self.field_array[16]['text'] = (GEM_CONF.swap_order_N_bits(((L_array[5] >> 24) & 0x1F), 5))
        self.field_array[17]['text'] = (GEM_CONF.swap_order_N_bits(((L_array[5] >> 16) & 0x1F), 5))
        self.field_array[18]['text'] = ((L_array[5] >> 8) & 0xF)
        self.field_array[19]['text'] = (GEM_CONF.swap_order_N_bits(((L_array[5] >> 0) & 0x1F), 5))
        self.field_array[20]['text'] = (GEM_CONF.swap_order_N_bits(((L_array[6] >> 24) & 0x1F), 5))
        self.field_array[21]['text'] = (GEM_CONF.swap_order_N_bits(((L_array[6] >> 16) & 0x3F), 6))
        self.field_array[22]['text'] = ((L_array[6] >> 8) & 0x1)
        self.field_array[23]['text'] = ((L_array[6] >> 0) & 0x1)
        self.field_array[24]['text'] = ((L_array[7] >> 16) & 0x3)
        self.field_array[25]['text'] = ((L_array[7] >> 8) & 0xF)
        self.field_array[26]['text'] = ((L_array[7] >> 0) & 0x1)
        self.field_array[27]['text'] = ((L_array[8] >> 24) & 0x7)
        self.field_array[28]['text'] = ((L_array[8] >> 16) & 0x1)
        self.field_array[29]['text'] = ((L_array[8] >> 8) & 0x3)
        self.field_array[30]['text'] = ((L_array[8] >> 0) & 0x1F)
        self.field_array[31]['text'] = ((L_array[9] >> 24) & 0x1)
        self.field_array[32]['text'] = ((L_array[9] >> 16) & 0x3F)
        self.field_array[33]['text'] = ((L_array[9] >> 8) & 0x1)
        self.field_array[34]['text'] = ((L_array[9] >> 0) & 0x3)
        self.field_array[35]['text'] = ((L_array[10] >> 24) & 0x1)
        self.field_array[36]['text'] = ((L_array[10] >> 16) & 0x3)
        for input, field in zip(self.input_array, self.field_array):
            if int(input.get()) != int(field['text']):
                input.config({"background": "Red"})
            else:
                input.config({"background": "White"})

    def read_TIGER_channel(self):
        TIGER_N = int(self.showing_TIGER.get())
        command_reply = self.GEMROC_reading_dict['{}'.format(self.showing_GEMROC.get())].GEM_COM.ReadTgtGEMROC_TIGER_ChCfgReg(self.GEMROC_reading_dict['{}'.format(self.showing_GEMROC.get())].c_inst, TIGER_N, int(self.Channel_IN.get()))

        L_array = array.array('I')  # L is an array of unsigned long
        L_array.fromstring(command_reply)
        L_array.byteswap()
        #
        for line in self.dict_pram_list:
            self.input_array[line].delete(0, END)
            self.input_array[line].insert(END, self.GEMROC_reading_dict['{}'.format(self.showing_GEMROC.get())].c_inst.Channel_cfg_list[int(self.showing_TIGER.get())][int(self.Channel_IN.get())][line])

        self.field_array[0]['text'] = ((L_array[1] >> 24) & 0x1)
        self.field_array[1]['text'] = ((L_array[1] >> 16) & 0x7)
        self.field_array[2]['text'] = ((L_array[1] >> 8) & 0x7)
        self.field_array[3]['text'] = ((L_array[1] >> 0) & 0x1)
        self.field_array[4]['text'] = ((L_array[2] >> 24) & 0x1)
        self.field_array[5]['text'] = (L_array[2] >> 16) & 0xF
        self.field_array[6]['text'] = ((L_array[2] >> 8) & 0xF)
        self.field_array[7]['text'] = ((L_array[2] >> 0) & 0x1)
        self.field_array[8]['text'] = ((L_array[3] >> 24) & 0x3)
        self.field_array[9]['text'] = ((L_array[3] >> 16) & 0x1F)
        self.field_array[10]['text'] = ((L_array[3] >> 8) & 0x3F)
        self.field_array[11]['text'] = ((L_array[3] >> 0) & 0x3F)
        self.field_array[12]['text'] = ((L_array[4] >> 24) & 0x1)
        self.field_array[13]['text'] = ((L_array[4] >> 16) & 0x7F)
        self.field_array[14]['text'] = ((L_array[4] >> 8) & 0x7F)
        self.field_array[15]['text'] = ((L_array[4] >> 0) & 0x1)
        self.field_array[16]['text'] = ((L_array[5] >> 24) & 0x1)
        self.field_array[17]['text'] = ((L_array[5] >> 16) & 0x1)
        self.field_array[18]['text'] = ((L_array[5] >> 8) & 0x1)
        self.field_array[19]['text'] = ((L_array[5] >> 0) & 0x7)
        self.field_array[20]['text'] = ((L_array[6] >> 24) & 0x3)
        self.field_array[21]['text'] = ((L_array[6] >> 16) & 0x7)
        self.field_array[22]['text'] = ((L_array[6] >> 8) & 0x3)
        self.field_array[23]['text'] = ((L_array[6] >> 0) & 0x1F)
        self.field_array[24]['text'] = ((L_array[7] >> 24) & 0x1F)
        self.field_array[25]['text'] = ((L_array[7] >> 16) & 0xF)
        self.field_array[26]['text'] = ((L_array[7] >> 8) & 0x3F)
        self.field_array[27]['text'] = ((L_array[7] >> 0) & 0x3)
        self.field_array[28]['text'] = ((L_array[8] >> 24) & 0x3)
        self.field_array[29]['text'] = ((L_array[8] >> 16) & 0x3)

        i = 0
        # for key, input in self.input_array.iteritems():
        #     if int(input.get()) != int(self.field_array[i]['text']):
        #         input.config({"background": "Red"})
        #         i += 1
        #     else:
        #         input.config({"background": "White"})

    def write_TIGER_GLOBAL(self):
        GEMROC = self.showing_GEMROC.get()
        TIGER = int(self.showing_TIGER.get())
        i = 0
        for key in self.label_array:
            self.GEMROC_reading_dict['{}'.format(GEMROC)].g_inst.Global_cfg_list[TIGER][key['text'].rstrip('\n')] = int(self.input_array[i].get())
            i += 1
        write = self.GEMROC_reading_dict['{}'.format(GEMROC)].GEM_COM.Set_param_dict_global(self.GEMROC_reading_dict[GEMROC].g_inst, "TxDDR", TIGER, 0)
        read = self.GEMROC_reading_dict['{}'.format(GEMROC)].GEM_COM.ReadTgtGEMROC_TIGER_GCfgReg(self.GEMROC_reading_dict[GEMROC].g_inst, TIGER)
        try:
            self.GEMROC_reading_dict['{}'.format(self.showing_GEMROC.get())].GEM_COM.global_set_check(write, read)
        except:
            self.error_led_update()

    def write_TIGER_GLOBAL_allGEM(self):
        for TIGER in range(0, 8):
            i = 0
            for key in self.label_array:
                self.GEMROC_reading_dict['{}'.format(self.showing_GEMROC.get())].g_inst.Global_cfg_list[int(TIGER)][key['text'].rstrip('\n')] = int(self.input_array[i].get())
                i += 1
            write = self.GEMROC_reading_dict['{}'.format(self.showing_GEMROC.get())].GEM_COM.Set_param_dict_global(self.GEMROC_reading_dict['{}'.format(self.showing_GEMROC.get())].g_inst, "TxDDR", int(TIGER), 0)
            read = self.GEMROC_reading_dict['{}'.format(self.showing_GEMROC.get())].GEM_COM.ReadTgtGEMROC_TIGER_GCfgReg(self.GEMROC_reading_dict['{}'.format(self.showing_GEMROC.get())].g_inst, int(TIGER))
            try:
                self.GEMROC_reading_dict['{}'.format(self.showing_GEMROC.get())].GEM_COM.global_set_check(write, read)
            except:
                self.error_led_update()

    def write_TIGER_GLOBAL_allsystem(self):
        for number, GEMROC in self.GEMROC_reading_dict.items():
            # print number
            for TIGER in range(0, 8):

                i = 0
                for key in self.label_array:
                    GEMROC.g_inst.Global_cfg_list[int(TIGER)][key['text'].rstrip('\n')] = int(self.input_array[i].get())
                    i += 1
                write = GEMROC.GEM_COM.Set_param_dict_global(GEMROC.g_inst, "TxDDR", int(TIGER), 0)
                read = GEMROC.GEM_COM.ReadTgtGEMROC_TIGER_GCfgReg(GEMROC.g_inst, int(TIGER))
                try:
                    GEMROC.GEM_COM.global_set_check(write, read)
                except:
                    self.error_led_update()

    def write_CHANNEL_Handling(self):
        if self.all_channels.get() == "All Channels":
            CHANNEL = 64
        else:
            CHANNEL = self.Channel_IN.get()
        if self.all_TIGERs.get() == "All TIGERs":
            TIGER_LIST = [0, 1, 2, 3, 4, 5, 6, 7]
        else:
            TIGER_LIST = [self.showing_TIGER.get()]
        for TIGER in TIGER_LIST:
            if self.all_GEMROCs.get() == "All GEMROCs":
                for number, GEMROC in self.GEMROC_reading_dict.items():
                    self.write_CHANNEL(GEMROC, TIGER, CHANNEL)
            else:
                print "TIGER {}".format(TIGER)
                self.write_CHANNEL(self.GEMROC_reading_dict['{}'.format(self.showing_GEMROC.get())], TIGER, CHANNEL)

    def write_CHANNEL(self, GEMROC, TIGER, CHANNEL, update_fields=True):
        TIGER = int(TIGER)
        CHANNEL = int(CHANNEL)
        if update_fields == True:
            for key, elem in self.input_array.iteritems():
                if CHANNEL != 64:
                    GEMROC.c_inst.Channel_cfg_list[TIGER][CHANNEL][key] = int(elem.get())
                else:
                    for CH in range(0, 64):
                        GEMROC.c_inst.Channel_cfg_list[TIGER][CH][key] = int(elem.get())

        if CHANNEL != 64:

            write = GEMROC.GEM_COM.WriteTgtGEMROC_TIGER_ChCfgReg(GEMROC.c_inst, TIGER, CHANNEL)
            read = GEMROC.GEM_COM.ReadTgtGEMROC_TIGER_ChCfgReg(GEMROC.c_inst, TIGER, CHANNEL)
            try:
                GEMROC.GEM_COM.channel_set_check_GUI(write, read)
            except:
                self.error_led_update()
                print "!!! ERROR IN CONFIGURATION  GEMROC {},TIGER {},CHANNEL {}!!!".format(GEMROC.GEM_COM.GEMROC_ID, TIGER, CHANNEL)
        else:
            failed = False

            for CH in range(0, 64):
                write = GEMROC.GEM_COM.WriteTgtGEMROC_TIGER_ChCfgReg(GEMROC.c_inst, TIGER, CH)
                read = GEMROC.GEM_COM.ReadTgtGEMROC_TIGER_ChCfgReg(GEMROC.c_inst, TIGER, CH)
                try:
                    GEMROC.GEM_COM.channel_set_check_GUI(write, read)
                except:
                    self.error_led_update()
                    failed = True
                    # print "!!! ERROR IN CONFIGURATION  GEMROC {},TIGER {},CHANNEL {}!!!".format(GEMROC.GEM_COM.GEMROC_ID, TIGER, CH)

            if failed:
                print "!!! ERROR IN CHANNEL CONFIGURATION  GEMROC {},TIGER {}!!!".format(GEMROC.GEM_COM.GEMROC_ID, TIGER)

    def load_thr_Handling(self, thr_target_entry, mode):
        thr_target = thr_target_entry.get()
        if thr_target == "This TIGER":
            TIGER = int(self.showing_TIGER.get())
            self.load_thr(source=mode, sigma=int(self.thr_sigma.get()), first=TIGER, last=TIGER + 1)
        if thr_target == "All TIGERs":
            self.load_thr(source=mode, sigma=int(self.thr_sigma.get()))
        if thr_target == "All TIGERs in all GEMROCs":
            self.load_thr(source=mode, sigma=int(self.thr_sigma.get()), to_all=True)

    def load_thr(self, to_all=False, source="auto", sigma=3, offset=0, first=0, last=8):
        if not to_all:
            GEMROC = self.GEMROC_reading_dict[self.showing_GEMROC.get()]
            print GEMROC
            for T in range(first, last):
                if source == "auto":
                    GEMROC.GEM_COM.Load_VTH_fromfile_autotuned(GEMROC.c_inst, T)
                if source == "scan":
                    GEMROC.GEM_COM.Load_VTH_fromfile(GEMROC.c_inst, T, sigma, offset)
                self.write_CHANNEL(GEMROC, T, 64, False)
        else:
            for number, GEMROC in self.GEMROC_reading_dict.items():
                for T in range(first, last):
                    if source == "auto":
                        GEMROC.GEM_COM.Load_VTH_fromfile_autotuned(GEMROC.c_inst, T)
                    if source == "scan":
                        GEMROC.GEM_COM.Load_VTH_fromfile(GEMROC.c_inst, T, sigma, offset)
                    self.write_CHANNEL(GEMROC, T, 64, False)

    def load_default_config(self):
        for number, GEMROC in self.GEMROC_reading_dict.items():
            for TIGER in range(0, 8):
                write = GEMROC.GEM_COM.Set_param_dict_global(GEMROC.g_inst, "TxDDR", int(TIGER), 0)
                read = GEMROC.GEM_COM.ReadTgtGEMROC_TIGER_GCfgReg(GEMROC.g_inst, int(TIGER))
                try:
                    GEMROC.GEM_COM.global_set_check(write, read)
                except:
                    self.error_led_update()
                self.write_CHANNEL(GEMROC, TIGER, 64, False)

    def Synch_reset(self, to_all=1):
        if to_all == 1:
            for number, GEMROC in self.GEMROC_reading_dict.items():
                GEMROC.GEM_COM.SynchReset_to_TgtFEB()
                GEMROC.GEM_COM.SynchReset_to_TgtTCAM()
                print "{} reset".format(number)
        else:
            GEMROC = self.showing_GEMROC.get()
            self.GEMROC_reading_dict[GEMROC].GEM_COM.SynchReset_to_TgtFEB()
            self.GEMROC_reading_dict[GEMROC].GEM_COM.SynchReset_to_TgtTCAM()
            print "{} reset".format(self.showing_GEMROC.get())

    def error_led_update(self, update=1):
        self.ERROR_LED["image"] = self.icon_bad
        if update == 1:
            self.main_window.after(5000, lambda: self.error_led_update(2))
        if update == 2:
            self.ERROR_LED["image"] = self.icon_off


def character_limit(entry_text):
    try:
        if int(entry_text.get()) < 0:
            entry_text.set(0)
        if int(entry_text.get()) > 63:
            entry_text.set(63)
    except:
        entry_text.set("")
        "Not valid input in channel field"


class GEMROC_HANDLER:
    def __init__(self, GEMROC_ID):
        self.GEMROC_ID = GEMROC_ID
        self.GEM_COM = COM_class.communication(GEMROC_ID, 0)  # Create communication class
        default_g_inst_settigs_filename = self.GEM_COM.conf_folder + sep + "TIGER_def_g_cfg_2018.txt"
        self.g_inst = GEM_CONF.g_reg_settings(GEMROC_ID, default_g_inst_settigs_filename)
        default_ch_inst_settigs_filename = self.GEM_COM.conf_folder + sep + "TIGER_def_ch_cfg_2018.txt"
        self.c_inst = GEM_CONF.ch_reg_settings(GEMROC_ID, default_ch_inst_settigs_filename)

    def __del__(self):
        self.GEM_COM.__del__()


Main_menu = menu()
Main_menu.runna()
