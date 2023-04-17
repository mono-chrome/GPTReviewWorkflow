```bicep
@description('Deployment Location')
param location string

@description('Prefix of Cosmos DB Resource Name')
param prefix string = enableCassandra ? 'coscas' : 'cosmos'

@description('Name of Cosmos DB Resource')
param name string = '${prefix}${uniqueString(resourceGroup().id, location)}'

@description('Max stale requests. Required for BoundedStaleness. Valid ranges, Single Region: 10 to 2147483647. Multi Region: 100000 to 2147483647.')
@minValue(10)
@maxValue(2147483647)
param maxStalenessPrefix int = 100000

@description('Max lag time (minutes). Required for BoundedStaleness. Valid ranges, Single Region: 5 to 84600. Multi Region: 300 to 86400.')
@minValue(5)
@maxValue(86400)
param maxIntervalInSeconds int = 300

@allowed([ 'Eventual', 'ConsistentPrefix', 'Session', 'BoundedStaleness', 'Strong' ])
@description('The default consistency level of the Cosmos DB account.')
param defaultConsistencyLevel string = 'Session'

@description('Enable system managed failover for regions')
param systemManagedFailover bool = true

@description('array of region objects or regions: [region: string]')
param secondaryLocations array = []

@description('Multi-region writes capability allows you to take advantage of the provisioned throughput for your databases and containers across the globe.')
param enableMultipleWriteLocations bool = true

@description('Enable Cassandra Backend.')
param enableCassandra bool = false

@description('Enable Serverless for consumption-based usage.')
param enableServerless bool = false

@description('Toggle to enable or disable zone redudance.')
param isZoneRedundant bool = false

var consistencyPolicy = {
  Eventual: {
    defaultConsistencyLevel: 'Eventual'
  }
  ConsistentPrefix: {
    defaultConsistencyLevel: 'ConsistentPrefix'
  }
  Session: {
    defaultConsistencyLevel: 'Session'
  }
  BoundedStaleness: {
    defaultConsistencyLevel: 'BoundedStaleness'
    maxStalenessPrefix: maxStalenessPrefix
    maxIntervalInSeconds: maxIntervalInSeconds
  }
  Strong: {
    defaultConsistencyLevel: 'Strong'
  }
}

var secondaryRegions = [for (region, i) in secondaryLocations: {
  locationName: contains(region, 'locationName') ? region.locationName : region
  failoverPriority: contains(region, 'failoverPriority') ? region.failoverPriority : i + 1
  isZoneRedundant: contains(region, 'isZoneRedundant') ? region.isZoneRedundant : isZoneRedundant
}]

var locations = union([
    {
      locationName: location
      failoverPriority: 0
      isZoneRedundant: isZoneRedundant
    }
  ], secondaryRegions)

var capabilities = union(
  enableCassandra ? [ { name: 'EnableCassandra' } ] : [],
  enableServerless ? [ { name: 'EnableServerless' } ] : []
)

resource cosmosDB 'Microsoft.DocumentDB/databaseAccounts@2022-05-15' = {
  name: toLower(name)
  location: location
  kind: 'GlobalDocumentDB'
  properties: {
    consistencyPolicy: consistencyPolicy[defaultConsistencyLevel]
    locations: locations
    databaseAccountOfferType: 'Standard'
    enableAutomaticFailover: systemManagedFailover
    enableMultipleWriteLocations: enableMultipleWriteLocations
    capabilities: capabilities
  }
}

@description('Cosmos DB Resource ID')
output id string = cosmosDB.id

@description('Cosmos DB Resource Name')
output name string = cosmosDB.name
```

```json
{
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
  "contentVersion": "1.0.0.0",
  "metadata": {
    "_generator": {
      "name": "bicep",
      "version": "0.16.2.56959",
      "templateHash": "6984401003152783394"
    }
  },
  "parameters": {
    "location": {
      "type": "string",
      "metadata": {
        "description": "Deployment Location"
      }
    },
    "prefix": {
      "type": "string",
      "defaultValue": "[if(parameters('enableCassandra'), 'coscas', 'cosmos')]",
      "metadata": {
        "description": "Prefix of Cosmos DB Resource Name"
      }
    },
    "name": {
      "type": "string",
      "defaultValue": "[format('{0}{1}', parameters('prefix'), uniqueString(resourceGroup().id, parameters('location')))]",
      "metadata": {
        "description": "Name of Cosmos DB Resource"
      }
    },
    "maxStalenessPrefix": {
      "type": "int",
      "defaultValue": 100000,
      "maxValue": 2147483647,
      "minValue": 10,
      "metadata": {
        "description": "Max stale requests. Required for BoundedStaleness. Valid ranges, Single Region: 10 to 2147483647. Multi Region: 100000 to 2147483647."
      }
    },
    "maxIntervalInSeconds": {
      "type": "int",
      "defaultValue": 300,
      "maxValue": 86400,
      "minValue": 5,
      "metadata": {
        "description": "Max lag time (minutes). Required for BoundedStaleness. Valid ranges, Single Region: 5 to 84600. Multi Region: 300 to 86400."
      }
    },
    "defaultConsistencyLevel": {
      "type": "string",
      "defaultValue": "Session",
      "metadata": {
        "description": "The default consistency level of the Cosmos DB account."
      },
      "allowedValues": [
        "Eventual",
        "ConsistentPrefix",
        "Session",
        "BoundedStaleness",
        "Strong"
      ]
    },
    "systemManagedFailover": {
      "type": "bool",
      "defaultValue": true,
      "metadata": {
        "description": "Enable system managed failover for regions"
      }
    },
    "secondaryLocations": {
      "type": "array",
      "defaultValue": [],
      "metadata": {
        "description": "array of region objects or regions: [region: string]"
      }
    },
    "enableMultipleWriteLocations": {
      "type": "bool",
      "defaultValue": true,
      "metadata": {
        "description": "Multi-region writes capability allows you to take advantage of the provisioned throughput for your databases and containers across the globe."
      }
    },
    "enableCassandra": {
      "type": "bool",
      "defaultValue": false,
      "metadata": {
        "description": "Enable Cassandra Backend."
      }
    },
    "enableServerless": {
      "type": "bool",
      "defaultValue": false,
      "metadata": {
        "description": "Enable Serverless for consumption-based usage."
      }
    },
    "isZoneRedundant": {
      "type": "bool",
      "defaultValue": false,
      "metadata": {
        "description": "Toggle to enable or disable zone redudance."
      }
    }
  },
  "variables": {
    "copy": [
      {
        "name": "secondaryRegions",
        "count": "[length(parameters('secondaryLocations'))]",
        "input": {
          "locationName": "[if(contains(parameters('secondaryLocations')[copyIndex('secondaryRegions')], 'locationName'), parameters('secondaryLocations')[copyIndex('secondaryRegions')].locationName, parameters('secondaryLocations')[copyIndex('secondaryRegions')])]",
          "failoverPriority": "[if(contains(parameters('secondaryLocations')[copyIndex('secondaryRegions')], 'failoverPriority'), parameters('secondaryLocations')[copyIndex('secondaryRegions')].failoverPriority, add(copyIndex('secondaryRegions'), 1))]",
          "isZoneRedundant": "[if(contains(parameters('secondaryLocations')[copyIndex('secondaryRegions')], 'isZoneRedundant'), parameters('secondaryLocations')[copyIndex('secondaryRegions')].isZoneRedundant, parameters('isZoneRedundant'))]"
        }
      }
    ],
    "consistencyPolicy": {
      "Eventual": {
        "defaultConsistencyLevel": "Eventual"
      },
      "ConsistentPrefix": {
        "defaultConsistencyLevel": "ConsistentPrefix"
      },
      "Session": {
        "defaultConsistencyLevel": "Session"
      },
      "BoundedStaleness": {
        "defaultConsistencyLevel": "BoundedStaleness",
        "maxStalenessPrefix": "[parameters('maxStalenessPrefix')]",
        "maxIntervalInSeconds": "[parameters('maxIntervalInSeconds')]"
      },
      "Strong": {
        "defaultConsistencyLevel": "Strong"
      }
    },
    "locations": "[union(createArray(createObject('locationName', parameters('location'), 'failoverPriority', 0, 'isZoneRedundant', parameters('isZoneRedundant'))), variables('secondaryRegions'))]",
    "capabilities": "[union(if(parameters('enableCassandra'), createArray(createObject('name', 'EnableCassandra')), createArray()), if(parameters('enableServerless'), createArray(createObject('name', 'EnableServerless')), createArray()))]"
  },
  "resources": [
    {
      "type": "Microsoft.DocumentDB/databaseAccounts",
      "apiVersion": "2022-05-15",
      "name": "[toLower(parameters('name'))]",
      "location": "[parameters('location')]",
      "kind": "GlobalDocumentDB",
      "properties": {
        "consistencyPolicy": "[variables('consistencyPolicy')[parameters('defaultConsistencyLevel')]]",
        "locations": "[variables('locations')]",
        "databaseAccountOfferType": "Standard",
        "enableAutomaticFailover": "[parameters('systemManagedFailover')]",
        "enableMultipleWriteLocations": "[parameters('enableMultipleWriteLocations')]",
        "capabilities": "[variables('capabilities')]"
      }
    }
  ],
  "outputs": {
    "id": {
      "type": "string",
      "metadata": {
        "description": "Cosmos DB Resource ID"
      },
      "value": "[resourceId('Microsoft.DocumentDB/databaseAccounts', toLower(parameters('name')))]"
    },
    "name": {
      "type": "string",
      "metadata": {
        "description": "Cosmos DB Resource Name"
      },
      "value": "[toLower(parameters('name'))]"
    }
  }
}
```