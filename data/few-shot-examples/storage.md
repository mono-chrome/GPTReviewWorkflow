```bicep
@description('Deployment Location')
param location string

@description('Name of Storage Account. Must be unique within Azure.')
param name string = 'st${uniqueString(resourceGroup().id, subscription().id)}'

@description('ID of the subnet where the Storage Account will be deployed, if virtual network access is enabled.')
param subnetID string = ''

@description('Toggle to enable or disable virtual network access for the Storage Account.')
param enableVNET bool = false

@description('Toggle to enable or disable zone redundancy for the Storage Account.')
param isZoneRedundant bool = false

@description('Storage Account Type. Use Zonal Redundant Storage when able.')
param storageAccountType string = isZoneRedundant ? 'Standard_ZRS' : 'Standard_LRS'

var networkAcls = enableVNET ? {
  defaultAction: 'Deny'
  virtualNetworkRules: [
    {
      action: 'Allow'
      id: subnetID
    }
  ]
} : {}

resource storageAccount 'Microsoft.Storage/storageAccounts@2022-09-01' = {
  name: name
  location: location
  sku: {
    name: storageAccountType
  }
  kind: 'StorageV2'
  properties: {
    encryption: {
      keySource: 'Microsoft.Storage'
      services: {
        blob: {
          enabled: true
        }
        file: {
          enabled: true
        }
      }
    }
    supportsHttpsTrafficOnly: true
    allowBlobPublicAccess: false
    networkAcls: networkAcls
    minimumTlsVersion: 'TLS1_2'
  }
}

@description('The ID of the created or existing Storage Account. Use this ID to reference the Storage Account in other Azure resource deployments.')
output id string = storageAccount.id
```

```json
{
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
  "contentVersion": "1.0.0.0",
  "metadata": {
    "_generator": {
      "name": "bicep",
      "version": "0.15.31.15270",
      "templateHash": "6249334553241462209"
    }
  },
  "parameters": {
    "location": {
      "type": "string",
      "metadata": {
        "description": "Deployment Location"
      }
    },
    "name": {
      "type": "string",
      "defaultValue": "[format('st{0}', uniqueString(resourceGroup().id, subscription().id))]",
      "metadata": {
        "description": "Name of Storage Account. Must be unique within Azure."
      }
    },
    "subnetID": {
      "type": "string",
      "defaultValue": "",
      "metadata": {
        "description": "ID of the subnet where the Storage Account will be deployed, if virtual network access is enabled."
      }
    },
    "enableVNET": {
      "type": "bool",
      "defaultValue": false,
      "metadata": {
        "description": "Toggle to enable or disable virtual network access for the Storage Account."
      }
    },
    "isZoneRedundant": {
      "type": "bool",
      "defaultValue": false,
      "metadata": {
        "description": "Toggle to enable or disable zone redundancy for the Storage Account."
      }
    },
    "storageAccountType": {
      "type": "string",
      "defaultValue": "[if(parameters('isZoneRedundant'), 'Standard_ZRS', 'Standard_LRS')]",
      "metadata": {
        "description": "Storage Account Type. Use Zonal Redundant Storage when able."
      }
    }
  },
  "variables": {
    "networkAcls": "[if(parameters('enableVNET'), createObject('defaultAction', 'Deny', 'virtualNetworkRules', createArray(createObject('action', 'Allow', 'id', parameters('subnetID')))), createObject())]"
  },
  "resources": [
    {
      "type": "Microsoft.Storage/storageAccounts",
      "apiVersion": "2022-09-01",
      "name": "[parameters('name')]",
      "location": "[parameters('location')]",
      "sku": {
        "name": "[parameters('storageAccountType')]"
      },
      "kind": "StorageV2",
      "properties": {
        "encryption": {
          "keySource": "Microsoft.Storage",
          "services": {
            "blob": {
              "enabled": true
            },
            "file": {
              "enabled": true
            }
          }
        },
        "supportsHttpsTrafficOnly": true,
        "allowBlobPublicAccess": false,
        "networkAcls": "[variables('networkAcls')]",
        "minimumTlsVersion": "TLS1_2"
      }
    }
  ],
  "outputs": {
    "id": {
      "type": "string",
      "value": "[resourceId('Microsoft.Storage/storageAccounts', parameters('name'))]",
      "metadata": {
        "description": "The ID of the created or existing Storage Account. Use this ID to reference the Storage Account in other Azure resource deployments."
      }
    }
  }
}
```
