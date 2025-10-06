### General requirements:

- [ ] The system must be built based on blockchain data structure.
- [ ] There is no administrator or central authority to manage or control the system.
- [ ] There are two types of users: public users and registered users (nodes)
- [ ] A user can add a new block to the chain if the block is successfully mined.
- [ ] When a transaction is created by a user, the transaction will be placed in a transactions pool.
- [ ] A user can always check the validation of the whole chain.
- [ ] A user can always check the validation of a specific block and add a validation flag to a valid block.
- [ ] The system must always validate the blockchain for any tamper on every reading or writing or any other operation on the blockchain.
- [ ] A user can see the data of every block.
- [ ] A user can see the information of the whole blockchain, including the number of blocks and the total number of transactions.
- [ ] A user can cancel of modify their own pending transactions on the pool.
### User interface:
- [ ] The application must have a textual console-based user interface
- [ ] The user interface must have a menu system to facilitate the operation of the application.
- [ ] The system should always keep users informed about what is going on. 
- [ ] User should be able to see the status of and some general information about the system, including the transactions, pool, blockchain, their profile, notifications, recent changes on the system, ongoing actions, etc.
- [ ] The UI should support undo and redo actions when entering data.
- [ ] User should have sufficient control and freedom on the system.
- [ ] Users should not have to wonder whether different words, situations, or actions mean the same thing.
- [ ] There must be reasonable communication with the user regarding the status of the system.
- [ ] Use should have enough contextual help related to the operations of the system.
### Public user
A public user is a user who is not registered or signed up in the application. This user has some limited access to the system.

- [ ] Any user can freely register (sign up) in the application.
- [ ] Any user can explore the public ledger and view the data of each block.
### Registration (Sign up):
Once a public user signed up in the application, a node is created for the user. We will call this user a “node user”, or “logged-in user”, or only a “node” for short.

- [ ] A user must provide a unique username and a password when registering in the system.
- [ ] A node user will receive 50 coins as a sign-up reward, after registration.
- [ ] A unique pair of private key and public key must be created for a node user, after registration.

### Node user (Logged in user)
This user can login to the system and perform some specific activities, such as transferring coin, mining a block, etc.
- [ ] A node user has a wallet.
- [ ] A node user can send some coins from their wallet to the other registered users in the system.
- [ ] A node user can receive some coins in their wallet from the other registered users in the system.
- [ ] A node user can try mining a new block.
- [ ] A node user can see their balance on the user page.
- [ ] A node user can see the history of their own transactions thorough a menu.
- [ ] A node user can view the current ongoing transactions on the pool

### Ledger (Blockchain data structure):
- [ ] Each block has a unique ID (a sequential number starting from Zero for the genesis block).
- [ ] Every block must contain a minimum of 5 and a maximum of 10 transactions, including the reward transactions.
### Transactions:
- [ ] An extra value could be placed on a transaction as transaction fee.
- [ ] A sender must enter the transaction fee, while creating a transaction.
- [ ] The transaction fee is incentive to motivate miners to pick a transaction for their new block.

### Data files
As shown in the Figure 1, there are three data files required for the system to meet the required functionalities. The purpose of each file is briefly described below:

- [ ] **The Database**
A relational database is required to store data of the registered users, including username, hash of password, private key, and public key, and more information if needed (e.g., recovery phrase key). It is obvious that this database must be securely implemented. This database must be used only for the users’ information and no data from the blockchain or the pool should be stored in the relational database.

- [ ] **The Ledger**
This is the main file to store all data of transactions. It must be developed according to requirements of blockchain data structure, including all the required components (for example, hash of block, metadata, transaction data, nonce, etc.)

- [ ] **The Pool**
As this application can serve only one user at a time, some changes of the blockchain (e.g., requests for transactions) needs to be temporarily placed in a file, until the validation process or consensus process is completed. The pool file is mainly used for this synchronization purpose.

This file contains a list of transactions, and its format must be according to the structure of the transactions (the same format with the ledger). Do not use a relational database, JSON, csv, XML, or any other similar standard data transmission protocols or format. (In the practicum 6, we have already discussed and learned how to save and load transactions on a file).

In the final assignment part 1, we have only **one instance of each file**, shared among all users (only one ledger, one user database, and only one pool). As at any specific time, only one user can access the file, it is not needed (and not allowed) to have a separate copy of files for each node.

### Mining:

- [ ] A new block could be mined, if there are a minimum of 5 valid transactions on the pool.
- [ ] A new block could be mined after the last block, only if every previous block in the chain has at least 3 valid flags.
- [ ] A block must be mined between 10 to 20 seconds. A proof of work is implemented for this purpose, which creates a specific hash with a specific number of leading zero. (This timing is for testing while assessing and grading your code. Do not use any sleep or delay function to adjust the time if it is too fast).
- [ ] A minimum of 3 minutes interval must be between every two consequent blocks.
- [ ] A miner will receive 50 coins, as a mining reward for a successful block added to the chain.

### Security:
- [ ] SHA256 must be used for any hashing in the system.
- [ ] A password must be saved in the form of a hash in the system.
- [ ] A user must be able to see their private key and public key when logged in.
- [ ] A username (or hashed unique public key) must be used as the public account number of a user for any transaction.