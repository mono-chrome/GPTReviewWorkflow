```bicep
@description('The location into which the resources should be deployed')
param location string

@minLength(3)
@maxLength(63)
@description('The name of the PostgreSQL server')
param name string = 'psql${uniqueString(resourceGroup().id, subscription().id, location)}'

@description('Database administrator login name')
@minLength(1)
param administratorLogin string

@description('Database administrator password')
@minLength(8)
@maxLength(128)
@secure()
param administratorLoginPassword string

@description('The tier of the particular SKU, e.g. Burstable')
@allowed([ 'Burstable', 'GeneralPurpose', 'MemoryOptimized' ])
param postgresFlexibleServersSkuTier string = 'Burstable'

@description('The name of the sku, typically, tier + family + cores, e.g. Standard_D4s_v3')
param postgresFlexibleServersSkuName string = 'Standard_B1ms'

@description('The version of a PostgreSQL server')
@allowed([ '11', '12', '13' ])
param postgresFlexibleServersversion string = '13'

@description('The mode to create a new PostgreSQL server')
@allowed([ 'Create', 'Default', 'PointInTimeRestore', 'Update' ])
param createMode string = 'Default'

@description('The size of the storage in GB')
@allowed([ 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384 ])
param storageSizeGB int = 32

@description('The number of days a backup is retained')
@minValue(7)
@maxValue(35)
param backupRetentionDays int = 7

@description('The geo-redundant backup setting')
@allowed([ 'Enabled', 'Disabled' ])
param geoRedundantBackup string = 'Disabled'

@description('The high availability mode')
@allowed([ 'Disabled', 'Enabled' ])
param highAvailability string = 'Disabled'

resource postgresFlexibleServers 'Microsoft.DBforPostgreSQL/flexibleServers@2022-12-01' = {
  name: name
  location: location
  sku: {
    name: postgresFlexibleServersSkuName
    tier: postgresFlexibleServersSkuTier
  }
  properties: {
    administratorLogin: administratorLogin
    administratorLoginPassword: administratorLoginPassword
    createMode: createMode
    storage: {
      storageSizeGB: storageSizeGB
    }
    backup: {
      backupRetentionDays: backupRetentionDays
      geoRedundantBackup: geoRedundantBackup
    }
    highAvailability: {
      mode: highAvailability
    }
    maintenanceWindow: {
      customWindow: 'Disabled'
      dayOfWeek: 0
      startHour: 0
      startMinute: 0
    }
    version: postgresFlexibleServersversion
  }
}
```

```json
{
    "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
    "contentVersion": "1.0.0.0",
    "metadata": {
        "_generator": {
            "name": "bicep",
            "version": "0.16.2.56959",
            "templateHash": "104214408982244982"
        }
    },
    "parameters": {
        "location": {
            "type": "string",
            "metadata": {
                "description": "The location into which the resources should be deployed"
            }
        },
        "name": {
            "type": "string",
            "defaultValue": "[format('psql{0}', uniqueString(resourceGroup().id, subscription().id, parameters('location')))]",
            "metadata": {
                "description": "The name of the PostgreSQL server",
                "minLength": 3,
                "maxLength": 63
            }
        },
        "administratorLogin": {
            "type": "string",
            "metadata": {
                "description": "Database administrator login name",
                "minLength": 1
            }
        },
        "administratorLoginPassword": {
            "type": "securestring",
            "metadata": {
                "description": "Database administrator password",
                "minLength": 8,
                "maxLength": 128
            }
        },
        "postgresFlexibleServersSkuTier": {
            "type": "string",
            "defaultValue": "Burstable",
            "metadata": {
                "description": "The tier of the particular SKU, e.g. Burstable",
                "allowedValues": [
                    "Burstable",
                    "GeneralPurpose",
                    "MemoryOptimized"
                ]
            }
        },
        "postgresFlexibleServersSkuName": {
            "type": "string",
            "defaultValue": "Standard_B1ms",
            "metadata": {
                "description": "The name of the sku, typically, tier + family + cores, e.g. Standard_D4s_v3"
            }
        },
        "postgresFlexibleServersversion": {
            "type": "string",
            "defaultValue": "13",
            "metadata": {
                "description": "The version of a PostgreSQL server",
                "allowedValues": [
                    "11",
                    "12",
                    "13"
                ]
            }
        },
        "createMode": {
            "type": "string",
            "defaultValue": "Default",
            "metadata": {
                "description": "The mode to create a new PostgreSQL server",
                "allowedValues": [
                    "Create",
                    "Default",
                    "PointInTimeRestore",
                    "Update"
                ]
            }
        },
        "storageSizeGB": {
            "type": "int",
            "defaultValue": 32,
            "metadata": {
                "description": "The size of the storage in GB",
                "allowedValues": [
                    32,
                    64,
                    128,
                    256,
                    512,
                    1024,
                    2048,
                    4096,
                    8192,
                    16384
                ]
            }
        },
        "backupRetentionDays": {
            "type": "int",
            "defaultValue": 7,
            "metadata": {
                "description": "The number of days a backup is retained",
                "minValue": 7,
                "maxValue": 35
            }
        },
        "geoRedundantBackup": {
            "type": "string",
            "defaultValue": "Disabled",
            "metadata": {
                "description": "The geo-redundant backup setting",
                "allowedValues": [
                    "Enabled",
                    "Disabled"
                ]
            }
        },
        "highAvailability": {
            "type": "string",
            "defaultValue": "Disabled",
            "metadata": {
                "description": "The high availability mode",
                "allowedValues": [
                    "Disabled",
                    "Enabled"
                ]
            }
        }
    },
    "resources": [
        {
            "type": "Microsoft.DBforPostgreSQL/flexibleServers",
            "apiVersion": "2022-12-01",
            "name": "[parameters('name')]",
            "location": "[parameters('location')]",
            "sku": {
                "name": "[parameters('postgresFlexibleServersSkuName')]",
                "tier": "[parameters('postgresFlexibleServersSkuTier')]"
            },
            "properties": {
                "administratorLogin": "[parameters('administratorLogin')]",
                "administratorLoginPassword": "[parameters('administratorLoginPassword')]",
                "createMode": "[parameters('createMode')]",
                "storage": {
                    "storageSizeGB": "[parameters('storageSizeGB')]"
                },
                "backup": {
                    "backupRetentionDays": "[parameters('backupRetentionDays')]",
                    "geoRedundantBackup": "[parameters('geoRedundantBackup')]"
                },
                "highAvailability": {
                    "mode": "[parameters('highAvailability')]"
                },
                "maintenanceWindow": {
                    "customWindow": "Disabled",
                    "dayOfWeek": 0,
                    "startHour": 0,
                    "startMinute": 0
                },
                "version": "[parameters('postgresFlexibleServersversion')]"
            }
        }
    ]
}
```