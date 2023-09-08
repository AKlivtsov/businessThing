from cx_Freeze import setup, Executable   

setup(   
    name = "BusinessThing",   
    version = "1.3",   
    description = "test",   
    executables = [Executable("launch.py")])