import pytest

@pytest.mark.e2e
def test_app_import_and_modes():
    # Importing here avoids importing textual unless running this test
    from src.goodchain import BlockchainApp, BlockchainExplorer, UserDashboardScreen

    # Assert modes are wired correctly without running the app
    assert isinstance(BlockchainApp.MODES, dict)
    assert BlockchainApp.MODES.get("blockchain_explorer") is BlockchainExplorer
    assert BlockchainApp.MODES.get("user_dashboard") is UserDashboardScreen

    # Instantiate the app (do not run event loop)
    app = BlockchainApp()
    # Ensure key bindings are present
    labels = [b[2] for b in getattr(app, "BINDINGS", [])]
    assert "Blockchain Explorer" in labels
    assert "User Dashboard" in labels
