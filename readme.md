# FedVDA official code

=====================

This repository contains the configuration files for FedAGit. The running code is available at [FedModule](https://github.com/desperadoccy/async-FL).

Please download the code from two repositories and place the configuration files from this repository into the `config` directory of the `FedModule` project. Then, execute the following command to start the experiment.

```bash
# base the root directory of the FedModule project
cd src/fl/
python main.py ../../config/FedAGit.json
```

=====================

This is the official code for the paper "FedAGit: Towards Efficient and Scalable Asynchronous Federated Learning via Stragglers Version Control".
