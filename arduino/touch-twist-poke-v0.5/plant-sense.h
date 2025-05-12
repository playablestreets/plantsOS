#ifndef PLANT_SENSE
#define PLANT_SENSE

#include <Arduino.h>
#include <EEPROM.h>
#include <cstdint>

#define NUMTOUCHES 12

#include "Adafruit_MPR121.h"

class PlantSense 
{
    public:
        enum MPR
        {
            MPR_ONE,
            MPR_TWO
        };
        enum config_reg
        {
            CONFIG1 = MPR121_CONFIG1,
            CONFIG2 = MPR121_CONFIG2
        };
        enum config_field
        {
            FIRST_FILTER_ITERATION,
            CHARGE_DISCHARGE_CURRENT, 
            CHARGE_DISCHARGE_TIME, 
            SECOND_FILTER_ITERATION, 
            ELECTRODE_SAMPLE_INTERVAL 
        };
        
        PlantSense()
        {
        }

        void init()
        {
            MPROne = Adafruit_MPR121();  // ADDR not connected: 0x5A
            MPRTwo = Adafruit_MPR121();  // ADDR tied to SDA:   0x5C

            bool MPROne_connected = false;
            bool MPRTwo_connected = false;

            //INIT MPR121
            while (!MPROne_connected) {
                if (!MPROne.begin(0x5A)) {
                    Serial.println("Left MPR121 not found, check wiring?");
                    delay(100);
                } else {
                    Serial.println("Left MPR121 found!");
                    MPROne_connected = true;
                }
            }

            while (!MPRTwo_connected) 
            {
                if (!MPRTwo.begin(0x5C)) 
                {
                    Serial.println("Right MPR121 not found, check wiring?");
                    delay(100);
                } 
                else 
                {
                    Serial.println("Right MPR121 found!");
                    MPRTwo_connected = true;
                }
            }
            
            // Some healthy defaults
            mpr_one_params.FFI = 3;
            mpr_one_params.CDC = 18;
            mpr_one_params.CDT = 4; 
            mpr_one_params.SFI = 0;
            mpr_one_params.ESI = 2;

            mpr_two_params = mpr_one_params;

            MPROne.writeRegister(
                    CONFIG1, 
                    pack_config1(
                        mpr_one_params.CDC, 
                        mpr_one_params.FFI)
                    );
            MPROne.writeRegister(
                    CONFIG2, 
                    pack_config2(
                        mpr_one_params.ESI, 
                        mpr_one_params.SFI, 
                        mpr_one_params.CDT)
                    );
            MPRTwo.writeRegister(
                    CONFIG1, 
                    pack_config1(
                        mpr_two_params.CDC, 
                        mpr_two_params.FFI)
                    );
            MPRTwo.writeRegister(
                    CONFIG2, 
                    pack_config2(
                        mpr_two_params.ESI, 
                        mpr_two_params.SFI, 
                        mpr_two_params.CDT)
                    );
        }

        /* This getter is passing values through for now
         * but it can provide the opportunity for inserting
         * more signal conditioning later without disrupting 
         * existing code flow
         */

		void write_eeprom()
		{
			uint16_t write_address = 0;
			bool eeprom_isset = true;
			EEPROM.put(write_address, eeprom_isset);
			write_address += sizeof(eeprom_isset);

			EEPROM.put(write_address, mpr_one_params);
			write_address += sizeof...(mpr_one_params);

			EEPROM.put(write_address, mpr_two_params);
		}

		bool read_eeprom_to_param_structs() {
			uint16_t read_address = 0;
			bool eeprom_isset = false;
			EEPROM.get(read_address, eeprom_isset);
			read_address += sizeof(eeprom_isset);

			if (eeprom_isset) {
				EEPROM.get(read_address, mpr_one_params);
				read_address += sizeof(mpr_one_params);

				EEPROM.get(read_address, mpr_two_params);
			}

			return eeprom_isset;
		}

        uint16_t read(MPR MPR_select, int i) 
        {
            if (MPR_select == PlantSense::MPR_ONE) 
            {
                return MPROne.filteredData(i);
            }
            return MPRTwo.filteredData(i);
        }

        void config(MPR MPR_select, config_field param, uint8_t value)
        {

            active_config = (MPR_select == PlantSense::MPR_ONE) 
                            ? mpr_one_params 
                            : mpr_two_params;

            uint8_t reg = 0;

            switch (param)
            {
                case FIRST_FILTER_ITERATION:
                    active_config.FFI = clip(value, 0, 3);
                    reg = CONFIG1;
                    break;
                case CHARGE_DISCHARGE_CURRENT:
                    active_config.CDC = clip(value, 1, 63);
                    reg = CONFIG1;
                    break;
                case CHARGE_DISCHARGE_TIME:
                    active_config.CDT = clip(value, 1, 7);
                    reg = CONFIG2;
                    break;
                case SECOND_FILTER_ITERATION:
                    active_config.SFI = clip(value, 0, 3);
                    reg = CONFIG2;
                    break;
                case ELECTRODE_SAMPLE_INTERVAL:
                    active_config.ESI = clip(value, 0, 7);
                    reg = CONFIG2;
                    break;
                default:
                    return;
            }

            uint8_t config_bitfield;

            if (reg == CONFIG1) {
                config_bitfield = pack_config1(
                        active_config.CDC, 
                        active_config.FFI
                        );
            }

            if (reg == CONFIG2) {
                config_bitfield = pack_config2(
                        active_config.ESI, 
                        active_config.SFI, 
                        active_config.CDT
                        );
            }

            if (MPR_select == MPR_ONE) 
            {
                mpr_one_params = active_config;
                MPROne.writeRegister(reg, config_bitfield);
            }
            if (MPR_select == MPR_TWO) 
            {
                mpr_two_params = active_config;
                MPRTwo.writeRegister(reg, config_bitfield);
            }
        }

    private:
        uint8_t clip(uint8_t value, uint8_t min, uint8_t max) 
        {
            value = (value > max) ? max : value;
            return (value < min) ? min : value;
        }
        
        // Packin' a cheeky bowl of bits
        uint8_t pack_config1(uint8_t CDC, uint8_t FFI) 
        {
            return (FFI << 6) | CDC; 
        }

        uint8_t pack_config2(uint8_t ESI, uint8_t SFI, uint8_t CDT)
        {
            return ((SFI << 3) | ESI) | (CDT << 5);
        }

        struct 
        {
            uint8_t FFI;
            uint8_t CDC;
            uint8_t CDT; 
            uint8_t SFI;
            uint8_t ESI;
        } mpr_one_params, mpr_two_params, active_config;

        Adafruit_MPR121 MPROne;  // ADDR not connected: 0x5A
        Adafruit_MPR121 MPRTwo;  // ADDR tied to SDA:   0x5C

};

#endif
