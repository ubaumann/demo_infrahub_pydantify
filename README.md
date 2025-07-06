---
tags:
  - topic
  - demo
  - codespaces
  - python
  - automation-stack
---

# Demo: Infrahub meets Pydantify


|             |                                                                                                                |
| ----------: | :--------------------------------------------------------------------------------------------------------------|
| Level       | beginner|intermediate|expert                                                                                   |
| Repo        | [https://github.com/NetAutLabs/demo_infrahub_pydantify](https://github.com/NetAutLabs/demo_infrahub_pydantify) |
| Discussion  | [Discussion GitHub Repo](https://github.com/NetAutLabs/demo_infrahub_pydantify/discussions)                    |
| Codespaces  | :material-check: [GitHub Codespaces](https://codespaces.new/NetAutLabs/demo_infrahub_pydantify)                |


This demo shows how [Infrahub Python transform](https://docs.infrahub.app/guides/python-transform) can be used to generate 
XML/JSON payload for Netconf/Restconf/gNMI as a artefact.
Nornir with the [nornir-conditional-runner](https://github.com/InfrastructureAsCode-ch/nornir_conditional_runner) is used
to configure the [containerlab](https://containerlab.dev/) topology. 


- `make setup`
- add repo as a read-only repository integration
  `infrahubctl repository add demo https://github.com/ubaumann/demo_infrahub_pydantify.git --read-only --ref main`
- `infrahubctl run infrahub/bootstrap/create_toplology.py leafs=3 spines=2 borders=2 routers=3 edges=1`


## Development

You can use uv to intstall all the dependencies:

```bash
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```
