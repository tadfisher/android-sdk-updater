class Package:
    def __init__(self, category, name, revision, semver, num=0):
        self.category = category
        self.name = name
        self.revision = revision
        self.semver = semver
        self.num = num

    def __str__(self):
        return '{0.name} [{0.revision}]'.format(self)
