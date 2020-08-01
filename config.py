from renko import RenkoSnapMode

class WindowShape:
    def __init__(self, past, future):
        self.past = past
        self.future = future
        self.combinedSize = past+future
        self.freeze = True

    def __setattr__(self, name, value):
        if hasattr(self, 'freeze'):
            raise Exception('WindowShape is immutable after initialisation')
        else:
            super(WindowShape, self).__setattr__(name, value)

    def __str__(self):
        return f'w{(self.past, self.future)}'


class Config:
    renkoSnapMode: RenkoSnapMode = RenkoSnapMode.SMALL
    window: WindowShape = WindowShape(3,1)
    utilDepth: int = 5
    debug: bool = False

    @staticmethod
    def getStringInfo():
        return f'''Configuration
        snapMode:      {Config.renkoSnapMode}
        windowShape:   {Config.window}
        utilDepth:     {Config.utilDepth}
        debug:         {Config.debug}
        '''