
if __name__ == "__main__":
    from services import InitializationService
    InitializationService.initialize_application()

    from ui import GoodchainApp
    app = GoodchainApp()
    app.run()
