from tkinter import *
from tkinter import font
import tkinter.ttk

from enum import Enum
from random import *

from functools import singledispatch
from inspect import *

from json import *

from sys import modules

from structures import (
    Size,
    Location,
    RectInfo
)

# 样式来自 Figma: Windows UI 3 (Community)
class Styles:
    class Fonts:
        IconStandard =                       ("Segoe Fluent Icons",                16,font.NORMAL)
        class English:
            Caption =                        ("Segoe UI Variable Small",           12,font.NORMAL)
            Body =                           ("Segoe UI Variable Text",            14,font.NORMAL)
            BodyStrong =                     ("Segoe UI Variable Text Semibold",   14,font.NORMAL)
            Subtitle =                       ("Segoe UI Variable Display Semibold",20,font.NORMAL)
            Title =                          ("Segoe UI Variable Display Semibold",28,font.NORMAL)
            TitleLarge =                     ("Segoe UI Variable Display Semibold",40,font.NORMAL)
            Display =                        ("Segoe UI Variable Display Semibold",68,font.NORMAL)
        class Chinese:
            Caption =                        ("Microsoft YaHei UI",                12,font.NORMAL)
            Body =                           ("Microsoft YaHei UI",                14,font.NORMAL)
            BodyStrong =                     ("Microsoft YaHei UI",                14,font.BOLD  )
            Subtitle =                       ("Microsoft YaHei UI",                20,font.BOLD  )
            Title =                          ("Microsoft YaHei UI",                28,font.BOLD  )
            TitleLarge =                     ("Microsoft YaHei UI",                40,font.BOLD  )
            Display =                        ("Microsoft YaHei UI",                68,font.BOLD  )
    class Colors:
        class Text:
            Primary =                        "#1B1B1B" 
            Secondary =                      "#606060"

            Hyperlink =                      "#003E92"
        class Background:
            ApplicationBackground =          "#F3F3F3"
            LayerAlt =                       "#FFFFFF"

            CardBackgroundDefault =          "#FCFCFC"   # Rest
            CardBackgroundSecondary =        "#F6F6F6"   # Pressed
            CardBackgroundTertiary =         "#FFFFFF"   # Hover
        class Strokes:
            CardStrokeColorSoild =           "#EBEBEB"
            Divider =                        "#E5E5E5"

class StylesTemplate:
    CardBase =  {
        'bg': Styles.Colors.Background.CardBackgroundDefault, 
        'highlightbackground': Styles.Colors.Strokes.CardStrokeColorSoild, 
        'highlightthickness': 1, 
        'padx': 16, 'pady': 16}

# 单例
class Singleton:
    # 获取某类型的对象，但全局唯一
    # t: 要获取对象的类型
    @staticmethod
    def GetInstance(t: type):
        __singleton_object_map = getattr(Singleton, "_singleton_object_map", dict())
        
        if __singleton_object_map == dict():
            __singleton_object_map[t] = t()

            setattr(Singleton, "_singleton_object_map", __singleton_object_map)
            return __singleton_object_map[t]
        
        if t not in __singleton_object_map:
            __singleton_object_map[t] = t()
            return __singleton_object_map[t]

        return __singleton_object_map[t]

    @staticmethod
    def Destroy(t: type):
        __singleton_object_map = getattr(Singleton, "_singleton_object_map", dict())
        if __singleton_object_map == dict():
            setattr(Singleton, "_singleton_object_map", __singleton_object_map)
            return
        
        if t not in __singleton_object_map:
            return
        
        del __singleton_object_map[t]
        setattr(Singleton, "_singleton_object_map", __singleton_object_map)

class PageBase:
    def __init__(self):
        self.appContainer: ApplicationContainer = Singleton.GetInstance(ApplicationContainer)
        super().__init__(self.appContainer.UIcontainer,width=1200,height=700-120, padx=40, pady=40)
        #StyleConfiger.configDefaultStyleOnControl(Frame(self,width=40)).pack(side=LEFT, fill=Y)
        #StyleConfiger.configDefaultStyleOnControl(Frame(self,height=40)).pack(side=TOP, fill=X)
        #StyleConfiger.configDefaultStyleOnControl(Frame(self,width=40)).pack(side=RIGHT, fill=Y)
        #StyleConfiger.configDefaultStyleOnControl(Frame(self,height=40)).pack(side=BOTTOM, fill=X)

        self.grid(row=0,column=0,sticky="nesw")

class JsonInitializer:
    FunctionT = type(lambda : None)
    def __init__(self):
        self.propSetter = {}
    
    def registerSetter(self, n: str, setter: FunctionT):
        if len(signature(setter).parameters) != 1:
            raise TypeError("argument 'setter' is wrong type")

        self.propSetter[n] = setter
    
    def __loadAndRaise(self, json):
        return loads(json)

    def initialize(self, json: str):
        json_obj = self.__loadAndRaise(json)

        for item in json_obj.items():
            key = item[0]
            value = item[1]
            if key not in self.propSetter:
                raise KeyError(f"Not registed initializer for '{key}' property.")
            
            self.propSetter[key](value)

class ControlMetadata(JsonInitializer):
    def __init__(self, layout):
        JsonInitializer.__init__(self)

        self.registerSetter("ClassName", lambda v: self.__setattr__("__className", v))
        self.registerSetter("Name", lambda v: self.__setattr__("Name", v))
        self.registerSetter("Properties", lambda v: self.__setattr__("__properties", v))

        self.initialize(layout)
    
    def createControlInstance(self):
        controlTy = modules[__name__].__getattr__(self.__getattribute__("__className"))
        instance = controlTy(dumps(self.__getattribute__("__properties")))
        instance.__setattr__("Name", self.__getattribute__("Name"))

        return instance

class ContainerBase(JsonInitializer):
    def __init__(self):
        self.__containerChildren: list[ControlMetadata] = []

        self.registerSetter("Children", lambda v: self.__childrenInitializer(v))
    
    def __childrenInitializer(self, l):
        pass

    def __getitem__(self, index: str):
        for i in self.__containerChildren:
            if i.Name == index:
                return i
        
        raise KeyError(f"Control of name `{index}` not found.")

# 整个程序的主要类型
class ApplicationContainer(Tk, JsonInitializer):
    def __init__(self, layout: str):
        Tk.__init__(self)
        JsonInitializer.__init__(self)

        self.registerSetter('Title', lambda v : self.title(v))
        
        def sizeChanger(prop, value):
            ri = RectInfo(self.geometry())
            ri.__setattr__(prop, value)
            self.geometry(str(ri))
            self.update()
            print(self.geometry())
            
        def setVisibility(b):
            if b:
                self.deiconify()
            else:
                self.iconify()

        self.registerSetter('Width', lambda v : sizeChanger('width', v))
        self.registerSetter('Height', lambda v : sizeChanger('height', v))
        self.registerSetter('X', lambda v : sizeChanger('x', v))
        self.registerSetter('Y', lambda v : sizeChanger('y', v))
        self.registerSetter("Resizable", lambda v : self.resizable(v[0], v[1]))
        self.registerSetter("MaxWidth", lambda v: self.maxsize(v, self.maxsize()[1]))
        self.registerSetter("MaxHeight", lambda v: self.maxsize((self.maxsize()[0], v)))
        self.registerSetter("MinWidth", lambda v: self.minsize(v, self.minsize()[1]))
        self.registerSetter("MinHeight", lambda v: self.minsize((self.minsize()[0], v)))
        self.registerSetter("Background", lambda v: self.config(bg = v))
        self.registerSetter("Visibility", lambda v: setVisibility(v))
        self.registerSetter("Title", lambda v: self.title(v))

        self.initialize(layout)
        self.mainloop()
        
class MFrame(Frame):
    def __init__(self, *a, **kw):
        Frame.__init__(self, *a, **kw)
        self.pack_propagate(False)

class TextBlock(Label):
    def __init__(self, parent: Misc, text: str | None = ..., font: font.Font | None = Styles.Fonts.English.Body, fg: str = Styles.Colors.Text.Primary, **a):
        Label.__init__(self, parent, text = text, font = font, fg = fg, **a)

class SeparatorDirection(Enum):
    horizontal = 0
    vertical = 1

HORIZONTAL_DIRECTION = SeparatorDirection.horizontal
VERTICAL_DIRECTION = SeparatorDirection.vertical

class Separator(MFrame):
    def __init__(self, parent: Misc, direction: SeparatorDirection, distance: int):
        Frame.__init__(self, parent)
        if direction is SeparatorDirection.horizontal:
            self.config(height=0,width=distance)
        elif direction is SeparatorDirection.vertical:
            self.config(height=distance,width=0)

if __name__ == '__main__':
    ApplicationContainer("""
{
    "X": 500,
    "Y": 300,
    "Width": 600,
    "Height": 600,
    "Resizable": [true, false],
    "MaxWidth": 800,
    "Title": "Hello my First Application"
}
""")