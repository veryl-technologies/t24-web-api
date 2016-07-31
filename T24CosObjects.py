class CosFrame:
    id = None
    parent_frames = []

    def __init__(self, element, parent_frames):
        self.id = element.get_attribute("id")
        self.name = element.get_attribute("name")
        self.src = element.get_attribute("src")
        self.parent_frames = parent_frames

    def __str__(self):
        if self.get_type() == "unk":
            return "Frame " + self.get_type() + " " + self.id + " " + self.src
        return "Frame " + self.get_type() + " " + self.id

    def get_type(self):
        if ".TABBED." in self.src:
            return "tab"
        if "OS.GET.MENU" in self.src:
            return "menu"
        if "OS.GET.TABBED.SCREEN" in self.src:
            return "tab"
        if "enqaction=SELECTION" in self.src:
            return "enq"
        return "unk"

class CosDivPane:
    id = None
    parent_frames = []

    def __init__(self, element, parent_frames):
        self.id = element.get_attribute("id")
        self.parent_frames = parent_frames

    def __str__(self):
        return "Div " + self.id