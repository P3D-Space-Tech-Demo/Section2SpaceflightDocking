
from panda3d.core import CardMaker, Shader, Vec3, Vec2, NodePath, ColorBlendAttrib

import random

class Explosion():
    cardMaker = None

    @staticmethod
    def getCard():
        if Explosion.cardMaker is None:
            Explosion.cardMaker = CardMaker("explosion maker")
            Explosion.cardMaker.setFrame(-1, 1, -1, 1)

        explosionCard = NodePath(Explosion.cardMaker.generate())

        return explosionCard

    def __init__(self, size, fireballBittiness, duration, starDuration, rotationRate = 0.2, expansionFactor = 7):
        self.explosionCard = Explosion.getCard()
        self.explosionCard.setScale(size)
        self.explosionCard.setBin("unsorted", 1)
        self.explosionCard.setDepthWrite(False)
        self.explosionCard.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.MAdd, ColorBlendAttrib.OIncomingAlpha, ColorBlendAttrib.OOne))
        self.explosionCard.setBillboardPointEye()

        shader = Shader.load(Shader.SL_GLSL, "Shaders/explosionVertex.glsl", "Shaders/explosionFragment.glsl")
        self.explosionCard.setShader(shader)

        self.explosionCard.setShaderInput("sourceTex1", loader.loadTexture("Shaders/noise1.png"))
        self.explosionCard.setShaderInput("sourceTex2", loader.loadTexture("Shaders/noise2.png"))

        self.explosionCard.setShaderInput("duration", duration)
        self.explosionCard.setShaderInput("expansionFactor", expansionFactor)
        self.explosionCard.setShaderInput("rotationRate", rotationRate)
        self.explosionCard.setShaderInput("fireballBittiness", fireballBittiness)
        self.explosionCard.setShaderInput("starDuration", starDuration)

        self.explosionCard.setShaderInput("randomisation1", Vec2(random.uniform(0, 1), random.uniform(0, 1)))
        self.explosionCard.setShaderInput("randomisation2", Vec2(random.uniform(0, 1), random.uniform(0, 1)))

        self.duration = duration
        self.starDuration = starDuration
        self.startTime = -1000
        self.explosionCard.setShaderInput("startTime", self.startTime)

        self.velocity = Vec3(0, 0, 0)

    def activate(self, velocity, pos):
        self.startTime = globalClock.getRealTime()
        self.explosionCard.setShaderInput("startTime", self.startTime)
        self.velocity = velocity
        self.explosionCard.reparentTo(render)
        self.explosionCard.setPos(pos)

    def update(self, dt):
        self.explosionCard.setPos(self.explosionCard.getPos() + self.velocity*dt)

    def isAlive(self):
        return (globalClock.getRealTime() - self.startTime) < (self.duration + self.starDuration)

    def cleanup(self):
        if self.explosionCard is not None:
            self.explosionCard.removeNode()
            self.explosionCard = None