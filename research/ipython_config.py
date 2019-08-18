# Configuration file for ipython.

c = get_config()

#------------------------------------------------------------------------------
# InteractiveShellApp(Configurable) configuration
#------------------------------------------------------------------------------

print("--------->>>>>>>> ENABLE AUTORELOAD <<<<<<<<<------------")
c.InteractiveShellApp.extensions = ['autoreload']
c.InteractiveShellApp.exec_lines = [
    '%autoreload 2',
    'print(f"Warning: disable autoreload in {__file__} to improve performance.")'
]
