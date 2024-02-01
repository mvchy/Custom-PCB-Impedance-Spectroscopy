
import scipy.io as sio
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy.fft import fft, fftfreq
from scipy.signal import find_peaks


def wrapTo180(input):
    logic_index = (input < - 180) | (180 < input)
    input[logic_index] = wrapTo360(input[logic_index]+180) - 180
    return input

def wrapTo360(input):
    positive_input = input > 0
    input = np.mod(input, 360)
    input[(input == 0) & positive_input] = 360
    return input

def wrapto2pi(input):
    positive_input = input > 0
    input = np.mod(input, 2 * np.pi)
    input[(input == 0) & positive_input] = 2 * np.pi
    return input

def readDatamat(data_set,pcb_amplifier_gain):
    #read Rknown value from .mat file
    R_gain = data_set['PGA1_gain']
    R_gain = R_gain[0,0]*10
    #read DUT value from .mat file
    DUT_gain = data_set['PGA0_gain']
    DUT_gain = DUT_gain[0,0]*10
    #read ADC sampling frequency value from .mat file 
    ADC_fs = data_set['adc_fs']
    ADC_fs = ADC_fs[0,0]
    #read generated sinusoidal signal frequency value from .mat file
    sine_freq = data_set['pattern_code']
    sine_freq = sine_freq[0,0]
    #read Rknown data (from ADC0 on PCB board) from .mat file
    data_R = data_set['data_ADC0']
    data_R_v = (data_R*3.3)/(2**16)                                     # normalise voltage 
    data_R_v = data_R_v[0]
    baseline_ADC0 = np.mean(data_R_v)                                   # shifting baseline
    data_R_v = -1*((data_R_v-baseline_ADC0)/(pcb_amplifier_gain))       # divided signal by PCB gain
    #read Rknown data (from ADC0 on PCB board) from .mat file
    data_DUT = data_set['data_ADC1']
    data_DUT_v = (data_DUT*3.3)/(2**16)                                 # normalise voltage 
    data_DUT_v = data_DUT_v[0]
    baseline_ADC1 = np.mean(data_DUT_v)                                 # shifting baseline
    data_DUT_v = -1*((data_DUT_v-baseline_ADC1)/(pcb_amplifier_gain))   # divided signal by PCB gain
    sample_number = data_DUT.size
    return R_gain,DUT_gain,ADC_fs,sine_freq,data_R_v,data_DUT_v,sample_number

def getPhase(fft_y):
    phase_list_rad = np.unwrap(np.angle(fft_y)[:sample_number//2])
    phase_wrap2pi = wrapto2pi(phase_list_rad)
    phase_list = np.degrees(phase_wrap2pi)
    return phase_list

def findFFT(ADC_fs,data_in,sample_number):
    T = 1.0 / ADC_fs
    fft_y = fft(data_in)
    
    frequency_list = fftfreq(sample_number, T)[:sample_number//2]
    magnitude_list = np.abs(fft_y)[:sample_number//2]
    phase_list_degree = getPhase(fft_y)
    return magnitude_list,phase_list_degree,frequency_list
    

folderName = "C:/Users/"                            # set directory of the folder containing .mat data files
excelName = 'C:/Users/'+'impedance_save'+'.xlsx'    # set pathway and name of excel file to read

fileName = pd.read_excel(excelName)

# Parameter from PCB and nxp firmware set up
num_test = 30
start_data_set = 0
end_data_set = start_data_set + num_test
Rknown_value = 1000
instrument_amp_gain = 10
lowpass_filter_gain = 1.5
pcb_amplifier_gain = instrument_amp_gain*lowpass_filter_gain
# read data file name
fileName_array = np.array(fileName)
data_set_name = fileName_array[start_data_set:end_data_set,0]


# sreate magnutude and phase arrays
DUT_spectrum_mag = np.zeros(num_test)
DUT_spectrum_phase = np.zeros(num_test)
R_spectrum_mag = np.zeros(num_test)
R_spectrum_phase = np.zeros(num_test)
imp_spectrum_mag = np.zeros(num_test)
imp_spectrum_phase = np.zeros(num_test)
imp_frequency_list = np.zeros(num_test)

for trial_num in np.arange(0,num_test,1):

    # get directory path
    matDirect = folderName+data_set_name[trial_num]
    print(matDirect)

    # Load mat file
    data_set = sio.loadmat(matDirect)

    # Read .mat file 
    R_gain,DUT_gain,ADC_fs,sine_freq,data_R_v,data_DUT_v,sample_number = readDatamat(data_set,pcb_amplifier_gain)

    # find Magnitude and phase by using FFT
    DUT_magnitude_list,DUT_phase_list_degree,DUT_frequency_list = findFFT(ADC_fs,data_DUT_v,sample_number)
    R_magnitude_list,R_phase_list_degree,R_frequency_list = findFFT(ADC_fs,data_R_v/Rknown_value,sample_number)

    # find peaks of FFT spectrum
    DUT_peaks, _ = find_peaks(DUT_magnitude_list, distance=100)
    R_peaks, _ = find_peaks(R_magnitude_list, distance=100)
    DUT_ind = np.argmax(DUT_magnitude_list[DUT_peaks])
    R_ind = np.argmax(R_magnitude_list[R_peaks])
    
    # save magnitude and phase valuses to arrays
    DUT_spectrum_mag[trial_num] = DUT_magnitude_list[DUT_peaks[DUT_ind]]
    DUT_spectrum_phase[trial_num] = DUT_phase_list_degree[DUT_peaks[DUT_ind]]
    R_spectrum_mag[trial_num] = R_magnitude_list[R_peaks[R_ind]]
    R_spectrum_phase[trial_num] = R_phase_list_degree[R_peaks[R_ind]]

    # convert to impedance
    imp_spectrum_mag[trial_num] =  (DUT_spectrum_mag[trial_num]/DUT_gain)/(R_spectrum_mag[trial_num]/R_gain)
    imp_spectrum_phase[trial_num] =  (DUT_spectrum_phase[trial_num]-R_spectrum_phase[trial_num])
    imp_frequency_list[trial_num] = sine_freq

    
imp_spectrum_phase = wrapTo180(imp_spectrum_phase)      # wrap phase shift in degree to (-180,180)

# plot bode 
f, (ax1, ax2) = plt.subplots(2, 1)
ax1.loglog(imp_frequency_list, imp_spectrum_mag,marker = 'o', ms = 10 )
ax2.semilogx(imp_frequency_list,imp_spectrum_phase,marker = 'o', ms = 10 )
ax1.set_title('Bode plot')
ax1.set_xlim(0,10**5)
ax1.set_xlabel('Frequency (Hz)')
ax1.set_ylabel('Magnitude Z (ohm)')
ax2.set_xlim(0,10**5)
ax2.set_xlabel('Frequency (Hz)')
ax2.set_ylabel('Phase (degree)')
ax1.grid()
ax2.grid()
plt.show()


