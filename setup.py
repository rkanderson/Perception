import cx_Freeze

executables = [cx_Freeze.Executable("main.py")]

cx_Freeze.setup(
    name="Perception",
    options={"build_exe": {"packages":["pygame", "math", "random"],
                           "include_files":["assets"]}},
    executables = executables

    )