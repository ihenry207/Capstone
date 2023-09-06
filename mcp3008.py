import machine

class MCP3008:
    def __init__(self, spi, cs, ref_voltage=3.3):
        """
        Creating MCP3008 instance
        
        cs:chip select pin
        ref_voltsge  is r
        spi: is the configured spi bus
        
        """
        self.cs = cs
        self.cs.value(1)  # ncs on
        self._spi = spi
        self._out_buf = bytearray(3)
        self._out_buf[0] = 0x01
        self._in_buf = bytearray(3)
        self._ref_voltage = ref_voltage

    def reference_voltage(self) -> float:
        """Returns the MCP3xxx's reference voltage as a float."""
        return self._ref_voltage

    def read(self, pin, is_differential=False):#here we will be reading from channel 0 or pin 0
        """
        read a voltage or voltage difference using the MCP3008.

        Args:
            pin: the pin to use
            is_differential: if true, return the potential difference between two pins,

        Returns:
            voltage in range [0, 1023] where 1023 = VREF (3V3)
        """
        self.cs.value(0)  # select and ready to communicate
        self._out_buf[1] = ((not is_differential) << 7) | (pin << 4)
        self._spi.write_readinto(self._out_buf, self._in_buf)
        self.cs.value(1)  # turn off or end communication
        return ((self._in_buf[1] & 0x03) << 8) | self._in_buf[2]