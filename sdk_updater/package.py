class Package:
    def __init__(self, category, name, revision, semver, num=0):
        self.category = category
        self.name = name
        self.revision = revision
        self.semver = semver
        self.num = num

    def __str__(self):
        return '{0.name} [{0.revision}]'.format(self)

    def __eq__(self, other):
        return self.name == other.name and self.semver == other.semver

    def __ne__(self, other):
        return not __eq__(other)

    def __hash__(self):
        const = 37
        total = 13
        total += self.name.__hash__() * total + const
        total += self.semver.__hash__() * total + const
        return total
