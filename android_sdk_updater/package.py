class Package:
    def __init__(self, category, name, revision, num=0):
        self.category = category
        self.name = name
        self.revision = revision
        self.num = num

    def __str__(self):
        return "[" + self.category + "] " + self.name + " " + str(self.revision)