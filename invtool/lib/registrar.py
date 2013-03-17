class Registrar():
    dns_dispatches = []
    dispatches = []

    def register(self, dispatch):
        self.dispatches.append(dispatch)

registrar = Registrar()
