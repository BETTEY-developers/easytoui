__all__ = [
    'Size',
    'Location',
    'RectInfo'
]

class Size:
    def __init__(self, width: int, height: int):
        (self.width, self.height) = (width, height)
    
    def __str__(self):
        return f"{self.width}x{self.height}"

class Location:
    def __init__(self, x: int, y: int):
        (self.x, self.y) = (x, y)
    
    def __str__(self):
        return f"{self.x}+{self.y}"

class RectInfo(Size, Location):
    def __init__(self, gemStr: str):
        Size.__init__(self, int(gemStr.split('x')[0]), int(gemStr.split('x')[1].split('+')[0]))
        Location.__init__(self, int(gemStr.split('+')[1]), int(gemStr.split('+')[2]))
    
    def __str__(self):
        return f"{Size.__str__(self)}+{Location.__str__(self)}"