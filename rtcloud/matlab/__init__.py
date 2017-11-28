import os
import matlab.engine

engine = matlab.engine.start_matlab()
engine.cd(os.path.dirname(os.path.realpath(__file__)))
engine.triarea(nargout=0)
