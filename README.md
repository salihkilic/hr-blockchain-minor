# hr-blockchain-minor

To run the Textual app, first install the development version of Textual in your terminal:

`pip install textual-dev`

Then run the Development Console with:

`textual console`

Install all requirements for the app with:
`pip install -r requirements.txt`

Go to the venv folder and activate the virtual environment with:
`.venv/Scripts/activate.bat`  (Windows)
or
`source .venv/bin/activate`  (MacOS / Linux)

And your app in another terminal window with:

`textual run --dev src/goodchain.py -- --node=1`

The `--node` argument specifies the node number to run.

> Each node uses its own local data directory containing a private copy of the ledger and transaction pool. Nodes
synchronize these states through network communication and consensus, not by sharing files. The user database is shared
between nodes to provide consistent user and key management. For this assignment, a user is assumed to be logged in on
only one node at a time; concurrent logins with the same user are not supported and multi-login safety is intentionally
not implemented.

Some nice links:

- [Textual Documentation](https://textual.textualize.io/)
- [Textual Widgets](https://textual.textualize.io/widget_gallery/)
- [Video Tutorials](https://www.youtube.com/@Textualize)
- Examples:
    - [Textual Examples (How-To)](https://github.com/Textualize/textual/tree/main/docs/examples)
    - [Textual Examples (Demos)](https://github.com/Textualize/textual/tree/main/examples)