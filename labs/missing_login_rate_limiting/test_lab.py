from labs.testing import LabContract as _LabContract
from .attack import demonstrate
class ScenarioTests(_LabContract):
    demonstrate = staticmethod(demonstrate)
del _LabContract
