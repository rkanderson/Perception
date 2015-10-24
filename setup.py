import cx_Freeze

executables = [cx_Freeze.Executable("main.py"), cx_Freeze.Executable("sound.py"), cx_Freeze.Executable("lvlconfigs.py")]

cx_Freeze.setup(
    name="Perception",
    options={"build_exe": {"packages":["pygame"],
                           "include_files":["racecar.png"]}},
    executables = executables

    )