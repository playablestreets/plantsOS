#ifndef PLANT_SENSE
#define PLANT_SENSE

#include <Arduino.h>

#define NUMTOUCHES 12

#include "Adafruit_MPR121.h"

/* This defines are in this range due to a clash with the Adafruit enum
 * I will re-do this interface once I've replaced the driver with 
 * something better
 */

#define MPR_ONE 0x90
#define MPR_TWO 0x91
#define FIRST_FILTER_ITERATION 0x92
#define CHARGE_DISCHARGE_CURRENT 0x93

#define CHARGE_DISCHARGE_TIME 0x94
#define SECOND_FILTER_ITERATION 0x95
#define ELECTRODE_SAMPLE_INTERVAL 0x96

class Plant_Sense 
{
    public:
    Plant_Sense()
    {
    }

    void init()
    {
        MPROne = Adafruit_MPR121();  // ADDR not connected: 0x5A
        MPRTwo = Adafruit_MPR121();  // ADDR tied to SDA:   0x5C

        MPROne_connected = false;
        MPRTwo_connected = false;

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


        mpr_one_params.FFI = 3;
        mpr_one_params.CDC = 18;
        mpr_one_params.CDT = 4; 
        mpr_one_params.SFI = 0;
        mpr_one_params.ESI = 2;

        mpr_two_params.FFI = 3;
        mpr_two_params.CDC = 18;
        mpr_two_params.CDT = 4; 
        mpr_two_params.SFI = 0;
        mpr_two_params.ESI = 2;
        
        uint8_t mpr1_config1 = (mpr_one_params.FFI << 6) | mpr_one_params.CDC; 
        uint8_t mpr2_config1 = (mpr_two_params.FFI << 6) | mpr_two_params.CDC; 

        uint8_t mpr1_config2 = (mpr_one_params.FFI << 3) | mpr_one_params.ESI;
        mpr1_config2         = mpr1_config2 | (mpr_one_params.CDT << 5); 
        
        uint8_t mpr2_config2 = (mpr_two_params.FFI << 3) | mpr_two_params.ESI;
        mpr2_config2         = mpr2_config2 | (mpr_two_params.CDT << 5); 

        MPROne.writeRegister(MPR121_CONFIG1, mpr1_config1);
        MPROne.writeRegister(MPR121_CONFIG2, mpr1_config2);
        
        MPRTwo.writeRegister(MPR121_CONFIG1, mpr2_config1);
        MPRTwo.writeRegister(MPR121_CONFIG2, mpr2_config2);
    }
    
    /* These getters are passing values through for now
     * but they can provide the opportunity for inserting
     * more signal conditioning later without disrupting 
     * existing code flow
     */
    
    uint16_t read(uint8_t MPR_select, int i) 
    {
        if (MPR_select == MPR_ONE) 
        {
            return MPROne.filteredData(i);
        }
        return MPRTwo.filteredData(i);
    }

    void config(uint8_t MPR_select, uint8_t param, uint8_t value)
    {
        uint8_t config_bitfield = 0;

        active_config = (MPR_select == MPR_ONE) ? mpr_one_params : mpr_two_params;

        uint8_t reg = 0;

        switch (param)
        {
            case FIRST_FILTER_ITERATION:
                active_config.FFI = clip(value, 0, 3);
                reg = MPR121_CONFIG1;
                break;
            case CHARGE_DISCHARGE_CURRENT:
                active_config.CDC = clip(value, 1, 63);
                reg = MPR121_CONFIG1;
                break;
            case CHARGE_DISCHARGE_TIME:
                active_config.CDT = clip(value, 1, 7);
                reg = MPR121_CONFIG2;
                break;
            case SECOND_FILTER_ITERATION:
                active_config.SFI = clip(value, 0, 3);
                reg = MPR121_CONFIG2;
                break;
            case ELECTRODE_SAMPLE_INTERVAL:
                active_config.ESI = clip(value, 0, 7);
                reg = MPR121_CONFIG2;
                break;
            default:
                return;
        }

        if (reg == MPR121_CONFIG1) {
            config_bitfield = (active_config.FFI << 6) | active_config.CDC; 
        }

        if (reg == MPR121_CONFIG2) {
            config_bitfield = (active_config.SFI << 3) | active_config.ESI;
            config_bitfield = config_bitfield | (active_config.CDT << 5);
        }

        if (MPR_select == MPR_ONE) 
        {
            mpr_one_params = active_config;
            MPROne.writeRegister(reg, config_bitfield);
        }
        else 
        {
            mpr_two_params = active_config;
            MPRTwo.writeRegister(reg, config_bitfield);
        }
    }

    private:
    uint8_t clip(uint8_t value, uint8_t min, uint8_t max) {
        value = (value > max) ? max : value;
        value = (value < min) ? min : value;
        return value;
    }

    // Some healthy defaults
    
    struct 
    {
        uint8_t FFI;
        uint8_t CDC;
        uint8_t CDT; 
        uint8_t SFI;
        uint8_t ESI;
    } mpr_one_params, mpr_two_params, active_config;

    
    // MPR121 CapTouch Breakout Stuff
    Adafruit_MPR121 MPROne;  // ADDR not connected: 0x5A
    Adafruit_MPR121 MPRTwo;  // ADDR tied to SDA:   0x5C

    bool MPROne_connected;
    bool MPRTwo_connected;
    

};

#endif
