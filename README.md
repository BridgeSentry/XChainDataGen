<h2><center>XChainDataGen (Fork): A Cross-Chain Dataset Generation Framework</center></h2>

<span><center>[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/release/python-3110/)</center></span>

This repository contains the code for XChainDataGen, a cross-chain dataset extraction and generation framework -- i.e., a tool that **extracts** cross-chain data from bridge contracts in multiple blockchains and **generates** datasets of cross-chain transactions (CCTX).

> [!WARNING]
> **This is a fork of the original XChainDataGen repository.** It contains additional features and improvements specific to the BridgeSentry project.
>
> The original repository can be found [here](https://github.com/AndreAugusto11/XChainDataGen), and is maintained by [@AndreAugusto11](https://github.com/AndreAugusto11).
>
> Original Paper: [https://arxiv.org/abs/2503.13637](https://arxiv.org/abs/2503.13637)

In this fork, we have added the following set of features, that are specific for building the dataset used in BridgeSentry:

- Support for additional bridges and blockchains (notably Nomad and PolyNetwork);
- Conversion of single-chain and cross-chain transactions into graph representations through a new `generate_graph_data` procedure;
- Integration with the BridgeSentry project for anomaly detection (which obtains the data from the PostgreSQL database);
- Creation of additional scripts for data cleaning procedures, and for manual addition of transactions from incidents with a smaller number of attack transactions (e.g. Qubit, Meterio, Hypr, ...);

### Project structure

```
.
├──.vscode/                          # Configurations to launch the application in VSCode
├── analysis/                        # R scripts for data analysis
│   ├── data/                        # Generated data in CSV format
│   ├── R Scripts/                   # R scripts for the analysis of data
│   ├── generate_csv.ipynb           # Extracts data from database and converts into CSV (saved in the `data` folder)
│   └── paper-visualizations.ipynb   # Main analysis of the data
├── cli/
│   └── cli.py                       # Command Line Interface
├── config/
│   ├── constants.py                 # File with the constants for the project (blockchains and bridges supported)
│   ├── rpcs_base_config.py          # List of public RPCs used for extracting data from each blockchain
│   └── rpcs_config.py               # File with the list of all available RPCs (i.e., returning 200), generated in runtime
├── extractor/
│   ├── across/                      # Data extraction logic for events emitted by across's contracts
│   │   ├── ABIs/
│   │   │   ├── arbitrum/            # The ABIs for each Across contract deployed in Arbitrum
│   │   │   └── avalanche/           # The ABIs for each Across contract deployed in Avalanche
│   │   │       ...
│   │   ├── constants.py             # Definition of all contract addresses, for all blockchains, and events of interest for each contract
│   │   ├── decoder.py               # A custom decoder for the events emitted by the contracts
│   │   └── handler.py               # Received a set of events, and stores in the database according to the defined schema
│   ├── ccip/                        # Data extraction logic for events emitted by ccip's contracts
│   │   └──  ...
│   ├── cctp/                        # Data extraction logic for events emitted by cctp's contracts
│   │   └──  ...
│   │   ...
│   ├── decoder.py                   # Base decoder logic
│   └── extractor.py                 # Base extraction logic
├── generator/
│   ├── common/                      # Cross-chain transaction generation logic for across
│   │   └──  price_generator.py      # Fetches token metadata and token prices for each token transacted
│   ├── across/                      # Cross-chain transaction generation logic for across
│   │   └── generator.py             # Cross-chain transaction generator for across
│   ├── ccip/                        # Cross-chain transaction generation logic for ccip
│   │   └── ...
│   ├── cctp/                        # Cross-chain transaction generation logic for cctp
│   │   └── ...
│   │   ...
│   └── generator.py                 # Base generation logic
├── graph_generator/
│   ├── ABI/                          # ABIs used to resolve function calls/logs when building graphs (e.g. ERC20 ABI)
│   ├── nomad/                        # Graph generation logic specific to the nomad bridge
│   │   └── graph_generator.py        # Builds per-chain and cross-chain graphs from the extracted/generated nomad data
│   ├── omnibridge/                   # Graph generation logic specific to the omnibridge bridge
│   │   └── ...
│   ├── polynetwork/                  # Graph generation logic specific to the polynetwork bridge
│   │   └── ...
│   ├── ronin/                        # Graph generation logic specific to the ronin bridge
│   │   └── ...
│   │   ...
│   ├── base_graph_generator.py       # Base logic shared by all bridge-specific graph generators (node/edge creation, cross-chain linking)
│   ├── generator.py                  # Dynamically loads the graph generator for the bridge being processed
│   ├── graph_class.py                # In-memory representation of a single-chain graph (nodes, edges, labels) before/after persisting it
│   ├── graph_label.py                # Enums for node/edge types and for blockchain-level and cross-chain-level labels (normal/anomaly)
│   ├── graph_utils.py                # Shared helpers (e.g. confirming/cleaning previously generated graph data)
│   ├── pricing.py                    # Fetches historical token prices used to compute the USD value of graph nodes/edges
│   └── token_inspector.py            # Resolves and caches ERC20 token metadata (symbol, name, decimals) for graph nodes
├── repository/
│   ├── across/                      # Implementation of repository pattern, with the definition of data models for across
│   │   ├── models.py                # Definition of data models for all relevant events
│   │   └── repository.py            # Definition of the repository for across
│   ├── ccip/                        # Implementation of repository pattern, with the definition of data models for ccip
│   │   └── ...
│   ├── cctp/                        # Implementation of repository pattern, with the definition of data models for cctp
│   │   └── ...
│   │   ...
│   ├── graphs/                      # Implementation of repository pattern, with the definition of data models for the heterogeneous graphs
│   │   ├── models.py                # Definition of the graph_mapping_blockchain, graph_mapping_cross_chain, graph_nodes and graph_edges tables
│   │   └── repository.py            # Definition of the repositories used by the graph_generator module
│   ├── base.py                      # Implementation of base repository, extended by all concrete implementations (CRUD operations)
│   └── database.py                  # Main logic for database creation
├── rpcs/
│   └── generate_rpc_configs.py      # Generate config file based on the public RPCs available for each blockchain
├── scripts/
│   ├── add_new_attacks_to_db.py     # Manually inserts cross-chain transactions (and their graphs) described in a YAML file into the database
│   ├── clean_dataset.py             # Flags noisy/unlinked graphs (e.g. destination-only graphs with no matching source) as not clean, via the discard_flag
│   └── template_manual_txs.yaml     # Template describing the expected YAML structure for manually-added incidents (see *_attack_txs.yaml for examples)
├── utils/                           # Datalog rules and facts
│   ├── rpc_utils.py                 # Management of RPC requests logic
│   └── utils.py                     # utils
└── __init__.py                      # Entry point of the application
```

## Data Extraction

The Extractor takes as input: (i) the bridge to be analyzed, (ii) a time interval defined using Unix timestamps, and (iii) a set of supported blockchains. The extraction process works as follows. It first loads the bridge configuration file, which specifies all relevant contract events for each blockchain where the bridge is deployed. The Extractor iterates over the user-specified blockchains, determining the nearest block numbers corresponding to the provided timestamps (i.e., the start and end blocks for each blockchain). It then divides this block range into intervals of 2,000 blocks and retrieves logs for all specified events in each contract using the eth_getLogs RPC method [./extractor/extractor.py](./extractor/extractor.py). For every captured event, the Extractor also fetches the corresponding transaction receipt and block information using _eth_getTransactionReceipt_ and _eth_getBlockByNumber_. Each event is decoded using either a base decoder [./extractor/decoder.py](./extractor/decoder.py) or, when necessary, a custom decoder tailored to the specific contract and event type. The extracted data is then stored in a storage system [./repository/database.py](./repository/database.py), with each event written as a separate relation. To ensure flexibility, we implemented a Repository Pattern [./repository/base.py](./repository/base.py), abstracting the data layer and allowing different storage systems. By modifying the database configuration file, users can customize the storage system based on their specific dataset requirements. At the end of the extraction phase, the storage system contains all the data associated with the specified bridge events and blockchains.

## CCTX Generation

The Generator builds cross-chain transactions based on previously extracted data. The base generator dynamically loads a custom generator for the bridge to be analyzed [./generator/generator.py](./generator/generator.py). In these custom components, the data previously extracted and written to the storage system is read, and the different records are merged in order to create cross-chain transactions. Records are merged based on cross-chain transaction identifiers (called deposit IDs, withdrawal IDs, or message IDs depending on the protocol), which link actions on both chains, also based on the sender, recipient, and tokens being transferred, which are always data available on both sides that can be used for linkability. The specific fields through which records are merged depend on the logic of each bridge. At the end of this phase, the storage system also contains datasets of cross-chain transactions.

## Graph Generation

On top of the extracted events and generated cross-chain transactions, the Graph Generator converts each on-chain transaction into a heterogeneous graph, and links the source- and destination-chain graphs of the same cross-chain transaction into a single cross-chain graph. The base generator dynamically loads a custom graph generator for the bridge to be analyzed [./graph_generator/generator.py](./graph_generator/generator.py), which extends the shared logic in [./graph_generator/base_graph_generator.py](./graph_generator/base_graph_generator.py). For every transaction, nodes are created for the entities involved (`user`, `router`, `token`, `other_account`, `log_event`, and `validator`) and edges are created for the relations between them (`transaction`, `token_transfer`, `token_auth`, `function_call`, `log_relation`, and `cross_chain_relation`), as defined in [./graph_generator/graph_label.py](./graph_generator/graph_label.py). Token metadata and historical USD prices are attached to the relevant nodes/edges using [./graph_generator/token_inspector.py](./graph_generator/token_inspector.py) and [./graph_generator/pricing.py](./graph_generator/pricing.py), respectively. Each graph is labelled as `normal` or `anomaly` at the single-chain level, and as `normal`, `anomaly_source`, `anomaly_offchain`, or `anomaly_destination` at the cross-chain level, based on a set of known attacker addresses supplied to the generator. The resulting nodes, edges, and mappings are persisted through the repositories defined in [./repository/graphs/](./repository/graphs/), in the `graph_nodes`, `graph_edges`, `graph_mapping_blockchain`, and `graph_mapping_cross_chain` tables, which are the tables consumed downstream by BridgeSentry for anomaly detection.

Because not every graph that gets generated ends up being linkable into a complete cross-chain transaction (e.g. a destination-chain event for which the matching source-chain event falls outside the extraction window), the `clean_graph_data` action and the [./scripts/clean_dataset.py](./scripts/clean_dataset.py) script can be used to flag such unlinked/noisy graphs through the `discard_flag` column, without deleting the underlying data. Note that not all single-chain unlinked graphs are necessarily noisy.

## A Quick Start (Docker)

The quick start leverages the [docker-compose.yaml](./docker-compose.yaml) file. It sets up a container running postgres, and the configuration for the application.

### Requirements

- Docker
- Docker Compose (optional for local PostgreSQL setup)

### Build & Start Containers

```bash
docker-compose up --build -d
```

The -d flag runs the containers in detached mode.

### Running XChainDataGen CLI Commands

>[!WARNING]
> Due to increased RPC and DUNE API restrictions, the extraction process may not work properly for all bridges and blockchains. To account for this, we have added a backup SQL dump of the data extracted for our BridgeSentry analysis, located at [dataset_dump_backup.sql](./dataset_dump_backup.sql). This dump can be restored to the PostgreSQL database using either DBeaver's GUI, or the following command:
>
>```bash
>pg_restore -U user -d db_app --clean --if-exists --no-owner dataset_dump_backup.sql # If targeting a local install
>pg_restore --no-owner --no-privileges -v -d "postgresql://user:password@localhost:5432/db_app" dataset_dump_backup.sql # If targeting using a URL connection string
>docker exec -i <container_name> pg_restore -U user -d db_app --no-owner < dataset_dump_backup.sql # If targeting from inside the container
>```
>
>⚠️ Keep in mind that these commands will overwrite any existing data in the database. The backup also contains the manually imported transaction data from the YAML files.


Extract the data related to a single bridge in multiple contracts using the following template:

```bash
docker-compose run --rm app extract --bridge <BRIDGE_NAME> --start_ts <START_TIMESTAMP> --end_ts <END_TIMESTAMP> --blockchains <BLOCKCHAIN_1> <BLOCKCHAIN_2> ... <BLOCKCHAIN_N>
```

To override the default data storage, use the `-e` flag to assign a new value to the environment variable DATABASE_URL (e.g., `-e DATABASE_URL=postgresql://user:password@db:5432/ccip`).

⚠️ Take into consideration that, depending on the number of contracts deployed for each bridge, on the number of events emitted by each in the interval of analysis, and the capabilities of your machine, this process can take long periods ⚠️

#### Cross-Chain Transaction Generator (~1 minute)

Generate cross-chain transactions, linking events and data across blockchains.

```bash
docker-compose run --rm app generate --bridge ccip
```

#### Graph Data Generator

Convert the extracted/generated data for a bridge into heterogeneous graphs, and link the source- and destination-chain graphs into cross-chain graphs. The `--start_ts`/`--end_ts` arguments are optional, and can be used to only generate graph data for a sub-interval of what was previously extracted.

```bash
docker-compose run --rm app generate_graph_data --bridge ronin --blockchains ethereum ronin [--start_ts XXXXXXXXX --end_ts XXXXXXXXX]
```

To flag graphs that could not be linked into a complete cross-chain transaction (optionally restricted to a single bridge):

```bash
docker-compose run --rm app clean_graph_data --bridge ronin
```

#### Retrieve Generated Data

Access the database container, and enter the database (the default database is `db_app`).

```bash
docker exec -it my_postgres psql -U user -d db_app
```

Run the `\d` command to list all relations in the database.

For CCIP, all cross-chain transactions will be in the ccip_cross_chain_transactions table.

```sql
select count(*) from ccip_cross_chain_transactions;
```

## Run locally

XChainDataGen can also be ran locally in your host machine.

### Requirements

- Postgres (v14)
- Python (v3.11.5)
- Virtualenv (optional)

#### Python & Virtualenv -- Installation Linux (Ubuntu)

```
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.11

sudo apt install python3.11-venv
```

#### Python & Virtualenv -- Installation MacOS

```
brew install python@3.11
pip install virtualenv
```

### Setup

Firstly, make sure Postgres is installed and you have a working database running in your own machine.

1. Create virtual environment `python3.11 -m venv .xchaindata`
2. Activate virstual environment `source .xchaindata/bin/activate`
3. Install all dependencies `pip install -r requirements.txt`
4. To stop using the env, run `deactivate`
5. Create a `.env` file setting the `DATABASE_URL` variable according to your database connection, and other remaining environment variables as specified in the `.env.template` file.

#### Using Terminal

### Data Extraction

```shell
python3.11 __init__.py extract --bridge <BRIDGE_NAME> --start_ts <START_TIMESTAMP> --end_ts <END_TIMESTAMP> --blockchains <BLOCKCHAIN_1> <BLOCKCHAIN_2> ... <BLOCKCHAIN_N>
```

### CCTX Generation

```shell
python3.11 __init__.py generate --bridge <BRIDGE_NAME>
```

### Graph Generation

```shell
python3.11 __init__.py generate_graph_data --bridge <BRIDGE_NAME> --blockchains <BLOCKCHAIN_1> <BLOCKCHAIN_2> ... <BLOCKCHAIN_N> [--start_ts <START_TIMESTAMP>] [--end_ts <END_TIMESTAMP>]
```

### Cleaning Unlinked Graph Data

```shell
python3.11 __init__.py clean_graph_data [--bridge <BRIDGE_NAME>]
```

#### Using VSCode

1. Open the project in VS Code.
2. Make sure you have the Python extension installed.
3. Open the Command Palette (Cmd+Shift+P on macOS or Ctrl+Shift+P on Windows/Linux).
4. Type "Python: Select Interpreter" and choose the interpreter in your xchaindata virtual environment (python 3.11).
5. Open the Debug view (Ctrl+Shift+D or Cmd+Shift+D on Mac).
6. From the dropdown at the top of the Debug view, select one of the options:

```
* [Stargate] test
* [Stargate] generate cross-chain transactions
* [Across] test
* [Across] generate cross-chain transactions
* [Omnibridge] test
* [Omnibridge] generate cross-chain transactions
* [Ronin] test
* [Ronin] generate cross-chain transactions
* [CCTP] test
* [CCTP] generate cross-chain transactions
* [CCIP] test
* [CCIP] generate cross-chain transactions
* [Polygon] test
* [Polygon] generate cross-chain transactions
```

Click the green play button or press F5 to start debugging.

## Manually Adding Incidents

For incidents with too few attack transactions to be reliably picked up by the Extractor and Generator (e.g. Qubit, Meterio, Hypr), transactions and their graphs can instead be described by hand in a YAML file and inserted directly into the database. The expected structure -- the main interaction, any internal transactions, emitted events and their relations, and the cross-chain linking between a source and a destination transaction -- is documented in [./scripts/template_manual_txs.yaml](./scripts/template_manual_txs.yaml), and example incidents following this structure can be found alongside it (e.g. [./scripts/qubit_attack_txs.yaml](./scripts/qubit_attack_txs.yaml)).

Once a YAML file is filled in, it can be imported with:

```shell
python3.11 scripts/add_new_attacks_to_db.py scripts/<INCIDENT_NAME>_attack_txs.yaml
```

This script [./scripts/add_new_attacks_to_db.py](./scripts/add_new_attacks_to_db.py) creates the corresponding nodes, edges, and graph/cross-chain-transaction mappings described in the YAML file, assigning the `anomaly` label to any graph, and the `anomaly_source`/`anomaly_offchain`/`anomaly_destination` label to any cross-chain graph, that involves one of the attacker addresses.

## Contributing

# Results and Data Analysis

The analysis of data extracted between Jun 1, 2024 and December 31, 2024 can be found in [./analysis/paper-visualizations-and-tables-generation.ipynb](./analysis/paper-visualizations-and-tables-generation.ipynb) and in [./analysis/R%20Scripts/paper-visualizations.R](./analysis/R%20Scripts/paper-visualizations.R).

## Suggested Citation

This work is an extension of the research made by @AndreAugusto11. If using this repository, cite as:

```bibtex
@misc{augusto2025xchaindatagencrosschaindatasetgeneration,
      title={XChainDataGen: A Cross-Chain Dataset Generation Framework},
      author={André Augusto and André Vasconcelos and Miguel Correia and Luyao Zhang},
      year={2025},
      eprint={2503.13637},
      archivePrefix={arXiv},
      primaryClass={cs.CR},
      url={https://arxiv.org/abs/2503.13637},
}
```
