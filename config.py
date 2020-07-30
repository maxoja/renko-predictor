class Config:
    patternLength: int = 3
    futureLength: int = 1
    utilDepth: int = 5
    debug: bool = False

    @staticmethod
    def getStringInfo():
        return f'''Configuration
        windowShape: {Config.patternLength}, {Config.futureLength}
        utilDepth:     {Config.utilDepth}
        debug:         {Config.debug}
        '''