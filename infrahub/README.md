# Infrahub Setup

Check out [Infrahub Documentation](https://docs.infrahub.app/guides/installation) for details.

## Docker Compose

The docker compose is downloaded from:

```bash
curl https://infrahub.opsmill.io/ --output docker-compose.yaml
```


## Manual Setup

- Start Infrahub
```bash
@ubaumann ➜ /workspaces/infrahub (main) $ cd infrahub/
@ubaumann ➜ /workspaces/infrahub/infrahub (main) $ docker compose up -d
```

- Load simple interface schema
```bash
@ubaumann ➜ /workspaces/infrahub/infrahub (main) $ infrahubctl schema load simple_interface_schema.yaml 
 schema 'simple_interface_schema.yaml' loaded successfully
 1 schema processed in 13.767 seconds.
```


## Try X
```
query MyQuery {
  NetworkDevice {
    edges {
      node {
        hfid
        name {
          value
        }
        description {
          value
        }
      }
    }
  }
}
```

```
{
  "data": {
    "NetworkDevice": {
      "edges": [
        {
          "node": {
            "hfid": [
              "switch01"
            ],
            "name": {
              "value": "switch01"
            },
            "description": {
              "value": "My awesome imaginary access switch"
            }
          }
        },
        {
          "node": {
            "hfid": [
              "switch02"
            ],
            "name": {
              "value": "switch02"
            },
            "description": {
              "value": "My awesome imaginary second access switch"
            }
          }
        }
      ]
    }
  }
}
```


```
query MyQuery {
  NetworkInterface {
    edges {
      node {
        display_label
        name {
          value
        }
        management {
          value
        }
        mode {
          value
        }
        description {
          value
        }
        device {
          node {
            hfid
            display_label
          }
        }
      }
    }
  }
}
```



