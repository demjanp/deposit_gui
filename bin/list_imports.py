from deposit_gui import DGUIMain

import sys

if __name__ == '__main__':
	
	gui = DGUIMain()

results = [m.__name__ for m in sys.modules.values() if m]
results = sorted(results)
txt = ",\n".join(["'%s'" % (name) for name in results])
with open("imports.txt", "w") as f:
	f.write(txt)