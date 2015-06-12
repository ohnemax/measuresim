### MeasureSim

The MeasureSim tool provides a frontend for a detector simulation. It requires access to GPIO ports for simple pulse signals (counting) and access to an I2C Bus with a connected MCP4725 DAC for more complex spectrum simulations. Otherwise the software will not work properly, if at all.



#### Requirements
     
     - python-qt4
     - pyqt4-dev-tools
     - python-matplotlib
     - Adafruit Python Scripts

#### Spectrum Data
     Spectrum data is stored in the =spectra/= folder. You can add your own data if you like. It needs to have a .dat suffix. Data files contain a single channel count per line.  
