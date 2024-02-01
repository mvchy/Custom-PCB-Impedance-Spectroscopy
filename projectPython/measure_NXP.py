import struct
import time
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import serial
import scipy.io as sio
import openpyxl


def collect_time():
    dateTimeObj = datetime.now()
    current_date = dateTimeObj.strftime("%Y%m%d-%H%M%S")
    
    return current_date

def call_serial_NXP_initial():
    serNXP = serial.Serial() 
    serNXP.baudrate = 230400
    serNXP.port = 'COM8'
    serNXP.set_buffer_size(rx_size=128000)
    serNXP.timeout = 60
    print(serNXP)
    serNXP.open()
    serNXP.flush()
    print("(NXP) : connected")
    return serNXP



def plot_data_together(fig,timeArrray, data_R_voltage,data_DUT_voltage,header_freq_code):

    plt.ion()
    if fig == None:
        fig, axs = plt.subplots(2, 1)
        
    else:
        axs =fig.get_axes()
        axs[0].clear()
        axs[1].clear()
        
    axs[0].plot(timeArrray, data_R_voltage, linestyle='-.')    
    
    if header_freq_code >= 10000:
        upperLimit = 0.00025
    elif (header_freq_code >= 1000) & (header_freq_code < 10000):
        upperLimit = 0.0025
    else:
        upperLimit = 0.025
    
    axs[0].set_xlim(0,upperLimit)
    axs[0].set_xlabel('Time')
    axs[0].set_ylabel('Voltage')
    axs[0].grid(True)
    title_AD0 = 'ADC00 - Frequency = '+str(header_freq_code) + ' Hz'
    axs[0].set_title(title_AD0)
    

    axs[1].plot(timeArrray, data_DUT_voltage, color='C4', linestyle='-.')
    axs[1].set_xlabel('Time')
    axs[1].set_ylabel('Voltage')
    axs[1].grid(True)
    axs[1].set_title('ADC01')
    axs[1].set_xlim(0,upperLimit)

    
    fig.tight_layout()
    fig.canvas.draw()
    fig.canvas.flush_events()
    
    plt.show()
    return fig


def save_nxp_data(folderName,header_trial_id,header_freq_code,data_ADC0_store,data_R_voltage,data_ADC1_store,data_DUT_voltage,R_DUT,C_DUT):
    filename_date = collect_time()
    save_name_ADC = folderName+filename_date+"-ADC-t"+str(header_trial_id)+"-"+str(header_freq_code)+".mat"
    sio.savemat(save_name_ADC,{'timestamp':filename_date,'trial_id':header_trial_id,'pattern_code': header_freq_code,
    'data_ADC0': data_ADC0_store, 'data_ADC0_v':data_R_voltage,'data_ADC1': data_ADC1_store, 'data_ADC1_v':data_DUT_voltage,
    'R_DUT':R_DUT,'C_DUT':C_DUT})

def load_excel_file(excelName):
    bookImp = openpyxl.load_workbook(excelName)
    sheetImp = bookImp.active
    return bookImp, sheetImp


def send_byte_to_NXP(serNXP):
    
    send_byte = (37).to_bytes(1, byteorder='little')
    serNXP.write(send_byte)

    print('sending byte',str(send_byte))
    print('(NXP): ***** send trigger *****')
    

def send_reset_byte_to_NXP(serNXP):
    
    send_byte = (12).to_bytes(1, byteorder='little')
    serNXP.write(send_byte)

    print('sending byte',str(send_byte))
    print('(NXP): ***** send reset command *****')
    print('(NXP): ..... wating for restarting .....')
    time.sleep(10)
    serNXP.flush()
    serNXP.close()
    print('(NXP): ***** flush and close serial *****')



def main_measure_NXP(electrodeConfig,numFreq,log_file_name,folderName,excelName):
    #####################################
    ## Initialization
    #####################################
    
    print("###### CONNECT TO NXP ######")
    serNXP = call_serial_NXP_initial()
    
    
    #####################################

    
    bookImp = openpyxl.load_workbook(excelName)
    sheetImp = bookImp.active

    #####################################

    # set parameter for save
    inverting_amp_ratio = 1
    R_DUT = electrodeConfig
    # R_DUT = 'SEEG-D1-Pt test lowfreq'
    C_DUT = 0
    Iout_amp = '10u'
    # electrodeConfig = '-2E-SEEG-D1-Pt'

    fig = None

    # Measure impedance 3 times and with 'numFreq' sweeping frequencies range
    numTrial = 3

    for nTrial in np.arange(0,numTrial):

        time.sleep(1)
        serNXP.flush()
        
        time.sleep(3)
        send_byte_to_NXP(serNXP) # Send trigger to NXP to start measuring

        # Receive data of each frequenncy and then sweep from high to low frequencies
        for nFreq in np.arange(0,numFreq):

            print('(NXP): /////// Start receiving data ///////')

            # Receive trial number
            header_trial_id_byte = serNXP.read(size=2)
            header_trial_id= int.from_bytes(header_trial_id_byte, 'little')
            print('(NXP): Package number: ',header_trial_id)
            
            # Receive the sampling frequency
            header_adc_sample_byte = serNXP.read(size=4)
            header_adc_sample = int.from_bytes( header_adc_sample_byte, 'little')
            print('(NXP): ADC sampling Frequency: ',header_adc_sample)
            print(header_adc_sample)
            fs = header_adc_sample
            tPeriod = 1/fs
            timeArrray = np.arange(0,16384)*tPeriod

            # Receive generated sinusoidal signal frequency
            header_freq_code_byte = serNXP.read(size=4)
            header_freq_code = int.from_bytes( header_freq_code_byte, 'little')
            print('(NXP): Signal Frequency: ',header_freq_code)
            print(header_freq_code_byte)

            # Receive Programable gain (PGA0)
            PGA0_gain_byte = serNXP.read(size=4)
            PGA0_gain = int.from_bytes(PGA0_gain_byte, 'little')
            print('(NXP): PGA0_gain: ',PGA0_gain)
            
            # Receive Programable gain (PGA1)
            PGA1_gain_byte = serNXP.read(size=4)
            PGA1_gain = int.from_bytes(PGA1_gain_byte, 'little')
            print('(NXP): PGA1_gain: ',PGA1_gain)

            # Receive the number of sample
            header_sample_number_b = serNXP.read(size=4)
            header_sample_number = int.from_bytes(header_sample_number_b, 'little')
            print('(NXP): Sample number:',  header_sample_number )
            
            
            # start record ADC0
            print('(NXP): Start record ADC0')
            data_ADC0_store = np.empty((header_sample_number))
            data_R_voltage = np.empty((header_sample_number))

            # normalise 16 bit ADC data 
            for i in np.arange(0,header_sample_number):
                
                data_ADC0_byte = serNXP.read(size=2)
                data_ADC0_store[i] = float(int.from_bytes(data_ADC0_byte, 'little'))
                data_R = (data_ADC0_store[i]*3.3)/(2**16)
                data_R_voltage[i] = 1*(data_R)*(inverting_amp_ratio)
                


            # uint32 seperate from ADC0
            header_freq_code_byte_ADC1 = serNXP.read(size=4)
            [header_freq_code_ADC1] = struct.unpack("I", header_freq_code_byte_ADC1)
            

            # start record ADC1
            print('(NXP): Start record ADC01')
            data_ADC1_store = np.empty((header_sample_number))
            data_DUT_voltage = np.empty((header_sample_number))

            # normalise 16 bit ADC data 
            for i in np.arange(0,header_sample_number):
                
                data_ADC1_byte = serNXP.read(size=2)
                data_ADC1_store[i] = float(int.from_bytes(data_ADC1_byte, 'little'))
                data_DUT = (data_ADC1_store[i]*3.3)/(2**16)
                data_DUT_voltage[i] = 1*(data_DUT)*(inverting_amp_ratio)

                       
            # save received parameters and data to .mat file 
            filename_date = collect_time()
            print('(NXP): Time: ',filename_date)
            
            filename = filename_date+"-"+str(electrodeConfig)+"-t"+str(header_trial_id)+"-"+str(header_freq_code)+".mat"
            save_name_ADC = folderName+filename
             
            sio.savemat(save_name_ADC,{'timestamp':filename_date,'trial_id':header_trial_id,'adc_fs':header_adc_sample,'pattern_code': header_freq_code,
            'data_ADC0': data_ADC0_store, 'data_ADC0_v':data_R_voltage,'data_ADC1': data_ADC1_store, 'data_ADC1_v':data_DUT_voltage,
            'R_DUT':R_DUT,'C_DUT':C_DUT, 'Iout_amp':Iout_amp,'PGA0_gain':PGA0_gain,'PGA1_gain':PGA1_gain})

            # save received parameters and file names to .xlsx file
            save_excel_name = filename_date+"-ADC-t"+str(header_trial_id)+"-"+str(header_freq_code)+".mat"
            row = ((filename, header_freq_code, 0,0,0,0,0,0,R_DUT,C_DUT,Iout_amp,PGA0_gain,PGA1_gain))
            sheetImp.append(row)
            
            # write file name to log file (.txt)
            fig = plot_data_together(fig, timeArrray, data_R_voltage,data_DUT_voltage,header_freq_code)
            with open(log_file_name+'.txt', 'a') as f:
                f.write('\n'+ "(NXP) : SAVE FILE : " + filename)
            


    bookImp.save(excelName) 
    time.sleep(3)  
    plt.close('all')
    send_reset_byte_to_NXP(serNXP)
    
    reset_date = collect_time()
    with open(log_file_name+'.txt', 'a') as f:
                f.write('\n'+ "(NXP) : reset sendting to NXP : " + reset_date)
    print("###### NXP disconnected ######")    