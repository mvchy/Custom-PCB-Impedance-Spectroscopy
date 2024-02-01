# Project Title: Custom PCB impedance spectroscopy

## Description

The Portable Impedance Spectrum Measurement PCB Board is a cost-effective and portable design for measuring impedance spectra across custom frequency ranges.

&nbsp;<br>

### Example Results

The conference paper provides comprehensive results obtained from Deep Brain Stimulation (DBS) electrode impedance measurements conducted using this PCB impedance spectroscopy Board. More information about the experiment setup and example results can be found here.
(Link to paper -- A Portable and Low-cost Electrochemical Impedance Spectroscopy Platform for the Characterisation of Implantable Electrodes)

&nbsp;<br>

## Hardware

The Gerber and NC drill files for the PCB-based impedance measurement board are provided [here](Hardware).
- The voltage supply for this board is -5V and +5V, connected to the P1 terminal.
- The working electrode, counter electrode, and reference electrode are connected to the P2 terminal as labelled.
- A BOM (.pdf) file is provided in the repo.

&nbsp;<br>

## Firmware

The NXP FRDM-K64F development board has been selected to control the PCB board. The MCUXpresso IDE is used, and the SDK version is 2.10.0. The firmware for the MCU can be found [here](Firmware) 

&nbsp;<br>

## Python set-up

In this project, the data transmission is performed in Python. The environmental package and list are included in this repository. Before starting measurements, you can use `env-list.txt` to create an identical environment by

`conda create --name myenv --file env-list.txt`

&nbsp;<br>

## Data transmission

The data is transferred through the USB port. Before starting the measurement, please follow these steps:

- Create a folder to contain the saved data (.mat)
- Create an Excel file to save the filename and some parameters. The example Excel file `impedance_save.xlsx` is provided in this repo. Please note this part can be ignored; all the needed parameters are still saved into .mat files. However, without the Excel file, `Find_impedance_spectrum.py`, which is used for impedance calculation and plotting, will not work properly.
- The main script to run the impedance measurement is `measure_impedance.py`. Set some parameters before starting the measurement, including:

```python
electrodeDUT = "DBS-D1-Pt-Ag "          # set the electrode configuration. This will appear on the .mat filename and in the Excel file
electrodeConfig = "3E"                  # set the number of electrode configuration
log_file_name = 'logs_experiment'       # set the log file name
numFreq = 30                            # set the number of frequencies (same as the number of frequency set in MCU or NXP-k64f)
folderName = "C:/Users/"                # set directory to save . mat data for each frequency
excelName = 'C:/Users/'+'impedance_save'+'.xlsx'  # set pathway and name of excel file to save file name and some parameters set-up in the impedance measurement

```

- Change the NXP board's COM port in `measure_nxp.py` in the `call_serial_NXP_initial()` function.

&nbsp;<br>

The .mat file structure include:

| Parameter | Description | Parameter | Description |
| --- | --- | --- | --- |
| timestamp | Date-Time of measurement | trial_id | number of trials |
| pattern_code | frequency of injected current | adc_fs | the sampling rate of DAC and ADC |
| data_ADC1 | the voltage across DUT in binary | data_ADC0 | the voltage across Rknown in binary |
| data_ADC1_v | the voltage across DUT in voltage | data_ADC0_v | the voltage across Rknown in voltage |
| PGA0_gain: 5 | programmable gain for DUT | PGA1_gain: 5 | programmable gain for Rknown |
| R_DUT | Electrode configuration (set manually before starting each measurement condition) | Iout_amp | current amplitude (set manually on script) |

&nbsp;<br>

## Impedance spectrum calculation and visualisation

Run `Find_impedance_spectrum.py` to calculate and plot the impedance spectrum in Bode plot. Before starting the calculation, set the `folderName` and `excelName`.
