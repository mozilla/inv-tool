class Registrar():
    dispatches = []

    def register(self, dispatch):
        self.dispatches.append(dispatch)

registrar = Registrar()
