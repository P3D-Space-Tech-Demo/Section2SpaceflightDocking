
class Spawner():
    def __init__(self, data, pos, h, objIsEnemy):
        if isinstance(data, tuple):
            self.spawnObj = data[0](*data[1:])
        else:
            self.spawnObj = data()

        self.spawnObj.root.setPos(render, pos)
        self.spawnObj.root.setH(render, h)
        self.spawnObj.root.detachNode()

        self.objIsEnemy = objIsEnemy

        self.isReady = True

    def cleanup(self):
        if self.spawnObj is not None:
            self.spawnObj.cleanup()
            self.spawnObj = None

        self.isReady = False