


import time
from datetime import datetime
from measure_NXP import main_measure_NXP
import numpy as np

def collect_time():
    dateTimeObj = datetime.now()
    filename_date = dateTimeObj.strftime("%Y%m%d-%H%M%S")
    return filename_date

numCond = 10                            # set the number of measurement
electrodeDUT = "DBS-D1-Pt-Ag "          # set the electrode configuration. This will appear on the .mat filename and in exel file
electrodeConfig = "3E"                  # set the number of electrode configuration
log_file_name = 'logs_experiment'       # set the log file name
numFreq = 30                            # set the number of frequencies (same as the number of frequency set in MCU or NXP-k64f)
folderName = "C:/Users/"                # set directory to save . mat data for each frequency 
excelName = 'C:/Users/'+'impedance_save'+'.xlsx'  # set pathway and name of excel file to save file name and some parameters set-up in the mimpedance measurement

for nCondition in np.arange(0,numCond):

    input('Press ENTER to start after change electrode...')
    electrodeConfig = input('Electrode config:')
    electrodeDUT = input('Electrode DUT:')
    electrodeSetup = str(electrodeConfig)+ "-"+ str(electrodeDUT)
    print(electrodeSetup)
    time.sleep(5)
    
    # Write time and date of measurements

    with open(log_file_name+'.txt', 'a') as f:

        f.write('\n'+'\n'+ "##############  START MEASUREMENT condition "+" ############## " )
        f.write('\n'+ "ELECTRODE CONFIG: " + electrodeConfig +" // "+ electrodeDUT )
        
        current_time = collect_time()
        f.write('\n'+'\n'+ str(current_time)+ " - Start measure impedance  ")

    time.sleep(10)
    main_measure_NXP(electrodeSetup,numFreq,log_file_name,folderName,excelName)      # Start Measure impedance 3 times
    time.sleep(5)

    with open(log_file_name+'.txt', 'a') as f:

        f.write('\n'+'\n'+ "##############  Done MEASUREMENT ############## " )
        # f.write('\n'+ "DBS3 - Pt - Ag/Agcl"  )
        current_time = collect_time()
        f.write('\n'+'\n'+ str(current_time)+ " - Done measure impedance  ")

    print("############## Done measurement condition  ##############" )




