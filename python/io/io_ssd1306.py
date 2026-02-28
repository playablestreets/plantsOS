"""
PiicoDev SSD1306 OLED peripheral module for plantsOS
Implements OSC hooks for display control.
"""

from PiicoDev_SSD1306 import PiicoDev_SSD1306

class IO_SSD1306:
    """
    PiicoDev SSD1306 OLED display interface for plantsOS.
    OSC path: /<name>/<command> [args...]
    """
    def __init__(self, bus=None, address=0x3C):
        self.address = address
        self.name = "oled"  # Default OSC path: /oled/...
        self.device = None
        self.width = 128
        self.height = 64

    def setup(self):
        self.device = PiicoDev_SSD1306(width=self.width, height=self.height, addr=self.address)
        self.device.show()
        print(f"  {self.name}: PiicoDev SSD1306 initialized at 0x{self.address:02X}")

    def read_data(self):
        # Return display state (could be extended)
        return {"width": self.width, "height": self.height}

    def write_data(self, **kwargs):
        command = kwargs.get('command', '')
        args = kwargs.get('args', [])
        
        # Map OSC commands to display functions
        if command == 'clear':
            self.device.fill(0)
            self.device.show()
        elif command == 'text' and len(args) >= 3:
            # /oled/text <string> <x> <y>
            text = str(args[0])
            x = int(args[1])
            y = int(args[2])
            self.device.text(text, x, y, 1)
            self.device.show()
        elif command == 'pixel' and len(args) >= 2:
            # /oled/pixel <x> <y> [color]
            x = int(args[0])
            y = int(args[1])
            color = int(args[2]) if len(args) > 2 else 1
            self.device.pixel(x, y, color)
            self.device.show()
        elif command == 'line' and len(args) >= 4:
            # /oled/line <x0> <y0> <x1> <y1> [color]
            x0, y0, x1, y1 = map(int, args[:4])
            color = int(args[4]) if len(args) > 4 else 1
            self.device.line(x0, y0, x1, y1, color)
            self.device.show()
        elif command == 'rect' and len(args) >= 4:
            # /oled/rect <x> <y> <w> <h> [color]
            x, y, w, h = map(int, args[:4])
            color = int(args[4]) if len(args) > 4 else 1
            self.device.rect(x, y, w, h, color)
            self.device.show()
        elif command == 'fill_rect' and len(args) >= 4:
            # /oled/fill_rect <x> <y> <w> <h> [color]
            x, y, w, h = map(int, args[:4])
            color = int(args[4]) if len(args) > 4 else 1
            self.device.fill_rect(x, y, w, h, color)
            self.device.show()
        elif command == 'show':
            self.device.show()
        # Add more commands as needed
        else:
            print(f"Unknown OLED command: {command} {args}")

    def cleanup(self):
        self.device.fill(0)
        self.device.show()
