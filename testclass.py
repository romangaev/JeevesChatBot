class TestClass:
    def __init__(self, state):
        self.state = state
        self.data = {}
    def change_state(self, state):
        self.state=state
    def get_state(self):
        return self.state