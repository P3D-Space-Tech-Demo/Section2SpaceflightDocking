from direct.showbase.ShowBase import ShowBase

from direct.task import Task
from panda3d.core import Vec4, Vec3, Vec2
from panda3d.core import Shader
from panda3d.core import ClockObject
from panda3d.core import WindowProperties
from panda3d.core import CardMaker

import random

class Game(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        self.win.setClearColor(Vec4(0, 0, 0, 1))

        self.disableMouse()

        properties = WindowProperties()
        properties.setSize(1280, 750)
        self.win.requestProperties(properties)

        self.exitFunc = self.cleanup

        self.accept("space", self.explode)

        self.accept("f", self.toggleFrameRateMeter)
        self.showFrameRateMeter = False

        self.updateTask = taskMgr.add(self.update, "update")

        cardMaker = CardMaker("explosion maker")
        cardMaker.setFrame(-1, 1, -1, 1)

        self.explosionCard = render.attachNewNode(cardMaker.generate())
        self.explosionCard.setY(5)
        self.explosionCard.setScale(0.4)

        self.duration = 0.4

        shader = Shader.load(Shader.SL_GLSL, "blasterImpactVertex.glsl", "blasterImpactFragment.glsl")
        self.explosionCard.setShader(shader)
        self.explosionCard.setShaderInput("startTime", -1000)
        self.explosionCard.setShaderInput("sourceTex1", loader.loadTexture("noiseRadial1.png"))
        self.explosionCard.setShaderInput("sourceTex2", loader.loadTexture("noiseRadial2.png"))
        self.explosionCard.setShaderInput("duration", self.duration)
        self.explosionCard.setShaderInput("expansionFactor", 1)
        self.explosionCard.setShaderInput("randomisation1", 0)
        self.explosionCard.setShaderInput("randomisation2", 0)

        self.timer = 0

        '''shader = Shader.load(Shader.SL_GLSL, "explosionVertex.glsl", "explosionFragment.glsl")
        self.explosionCard.setShader(shader)
        self.explosionCard.setShaderInput("startTime", -1000)
        self.explosionCard.setShaderInput("sourceTex1", loader.loadTexture("noise1.png"))
        self.explosionCard.setShaderInput("sourceTex2", loader.loadTexture("noise2.png"))
        self.explosionCard.setShaderInput("duration", 1.25)
        self.explosionCard.setShaderInput("starDuration", 1)
        self.explosionCard.setShaderInput("expansionFactor", 7)
        self.explosionCard.setShaderInput("rotationRate", 0.2)
        self.explosionCard.setShaderInput("fireballBittiness", 1.5)
        self.explosionCard.setShaderInput("randomisation1", Vec2(0, 0))
        self.explosionCard.setShaderInput("randomisation2", Vec2(0, 0))'''

        '''self.explosionCard = render.attachNewNode(cardMaker.generate())
        self.explosionCard.setY(5)
        self.explosionCard.setX(-1.125)

        shader = Shader.load(Shader.SL_GLSL, "explosionVertex.glsl", "explosionFragment.glsl")
        self.explosionCard.setShader(shader)
        self.explosionCard.setShaderInput("startTime", -1000)
        self.explosionCard.setShaderInput("sourceTex1", loader.loadTexture("noise1.png"))
        self.explosionCard.setShaderInput("sourceTex2", loader.loadTexture("noise2.png"))
        self.explosionCard.setShaderInput("duration", 1.25)
        self.explosionCard.setShaderInput("starDuration", 1)
        self.explosionCard.setShaderInput("expansionFactor", 7)
        self.explosionCard.setShaderInput("rotationRate", 0.2)
        self.explosionCard.setShaderInput("fireballBittiness", 1.5)
        self.explosionCard.setShaderInput("randomisation1", Vec2(0, 0))
        self.explosionCard.setShaderInput("randomisation2", Vec2(0, 0))

        self.explosionCard2 = render.attachNewNode(cardMaker.generate())
        self.explosionCard2.setY(5)
        self.explosionCard2.setX(1.125)

        shader = Shader.load(Shader.SL_GLSL, "explosionVertex.glsl", "explosionFragment_OLD.glsl")
        self.explosionCard2.setShader(shader)
        self.explosionCard2.setShaderInput("startTime", -1000)
        self.explosionCard2.setShaderInput("sourceTex1", loader.loadTexture("noise1.png"))
        self.explosionCard2.setShaderInput("sourceTex2", loader.loadTexture("noise2.png"))
        self.explosionCard2.setShaderInput("duration", 1.25)
        self.explosionCard2.setShaderInput("starDuration", 1)
        self.explosionCard2.setShaderInput("expansionFactor", 7)
        self.explosionCard2.setShaderInput("rotationRate", 0.2)
        self.explosionCard2.setShaderInput("fireballBittiness", 1.5)
        self.explosionCard2.setShaderInput("randomisation1", Vec2(0, 0))
        self.explosionCard2.setShaderInput("randomisation2", Vec2(0, 0))'''

    def explode(self):
        self.explosionCard.setShaderInput("randomisation1", random.uniform(0, 3.152))
        self.explosionCard.setShaderInput("randomisation2", random.uniform(0, 3.152))
        self.explosionCard.setShaderInput("startTime", globalClock.getRealTime())

        '''self.explosionCard.setShaderInput("randomisation1", Vec2(random.uniform(0, 1), random.uniform(0, 1)))
        self.explosionCard.setShaderInput("randomisation2", Vec2(random.uniform(0, 1), random.uniform(0, 1)))
        self.explosionCard.setShaderInput("startTime", globalClock.getRealTime())'''

        '''self.explosionCard2.setShaderInput("randomisation1", Vec2(random.uniform(0, 1), random.uniform(0, 1)))
        self.explosionCard2.setShaderInput("randomisation2", Vec2(random.uniform(0, 1), random.uniform(0, 1)))
        self.explosionCard2.setShaderInput("startTime", globalClock.getRealTime())'''

    def update(self, task):
        dt = globalClock.getDt()

        self.timer -= dt
        if self.timer <= 0:
            self.timer = self.duration + 0.1
            self.explode()

        return Task.cont

    def toggleFrameRateMeter(self):
        self.showFrameRateMeter = not self.showFrameRateMeter

        self.setFrameRateMeter(self.showFrameRateMeter)

    def cleanup(self):
        pass

    def quit(self):
        self.cleanup()

        base.userExit()

game = Game()
game.run()
