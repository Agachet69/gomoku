




import yappi

yappi.start()

from gomoku import *

yappi.stop()
yappi.get_func_stats().save("main.prof", type="PSTAT")