```bicep
@description('Optional. Name for the Event Hub cluster, Alphanumerics and hyphens characters, Start with letter, End with letter or number.')
param clusterName string = 'null'

@description('Optional. The quantity of Event Hubs Cluster Capacity Units contained in this cluster.')
param clusterCapacity int = 1

@description('Optional. Location for all resources.')
param location string = resourceGroup().location

@description('Optional. Tags of the resource.')
param tags object = {}

@description('''Optional. The name of the event hub namespace to be created.
Below paramters you can pass while creating the Azure Event Hub namespace.
sku: (Optional) Possible values are "Basic" or "Standard" or "Premium". Detault to 'Standard'.
capacity: (Optional) int, The Event Hubs throughput units for Basic or Standard tiers, where value should be 0 to 20 throughput units.The Event Hubs premium units for Premium tier, where value should be 0 to 10 premium units. Default to 1.
zoneRedundant: (Optional) bool, Enabling this property creates a Standard Event Hubs Namespace in regions supported availability zones. Default to false.
isAutoInflateEnabled: (Optional) bool,  Value that indicates whether AutoInflate is enabled for eventhub namespace. Only available for "Standard" sku. Default to false.
maximumThroughputUnits: (Optional) int, Upper limit of throughput units when AutoInflate is enabled, value should be within 0 to 20 throughput units. ( '0' if AutoInflateEnabled = true)
disableLocalAuth: (Optional) bool, This property disables SAS authentication for the Event Hubs namespace. Default to false.
kafkaEnabled: (Optional) bool, Value that indicates whether Kafka is enabled for eventhub namespace. Default to true.
''')
param eventHubNamespaces object = {}

var varEventHubNamespaces = [for eventHubnamespace in items(eventHubNamespaces): {
  eventHubNamespaceName: eventHubnamespace.key
  sku: contains(eventHubnamespace.value, 'sku')? eventHubnamespace.value.sku : 'Standard'
  capacity: contains(eventHubnamespace.value, 'capacity') ? eventHubnamespace.value.capacity: 1
  zoneRedundant: contains(eventHubnamespace.value, 'zoneRedundant') ? eventHubnamespace.value.zoneRedundant : false
  isAutoInflateEnabled: contains(eventHubnamespace.value, 'isAutoInflateEnabled') ? eventHubnamespace.value.isAutoInflateEnabled: false
  maximumThroughputUnits: contains(eventHubnamespace.value, 'maximumThroughputUnits') ? eventHubnamespace.value.maximumThroughputUnits: 0
  disableLocalAuth: contains(eventHubnamespace.value, 'disableLocalAuth') ? eventHubnamespace.value.disableLocalAuth: false
  kafkaEnabled: contains(eventHubnamespace.value, 'kafkaEnabled') ? eventHubnamespace.value.kafkaEnabled: true
}]

resource cluster 'Microsoft.EventHub/clusters@2021-11-01' = if (clusterName != 'null' )  {
  name: clusterName
  location: location
  tags: tags
  sku: {
    name: 'Dedicated'
    capacity: clusterCapacity
  }
  properties: {}
  dependsOn: [
    resourceGroup()
  ]
}

resource eventHubNamespace 'Microsoft.EventHub/namespaces@2021-11-01' = [for varEventHubNamespace in varEventHubNamespaces: if (!empty(eventHubNamespaces)) {
  name: varEventHubNamespace.eventHubNamespaceName
  location: location
  sku: {
    name: varEventHubNamespace.sku
    tier: varEventHubNamespace.sku
    capacity: varEventHubNamespace.capacity
  }
  properties: {
    disableLocalAuth: varEventHubNamespace.disableLocalAuth
    kafkaEnabled: varEventHubNamespace.kafkaEnabled
    isAutoInflateEnabled: varEventHubNamespace.isAutoInflateEnabled
    maximumThroughputUnits: ((varEventHubNamespace.isAutoInflateEnabled) ? varEventHubNamespace.maximumThroughputUnits : 0)
    zoneRedundant: varEventHubNamespace.zoneRedundant
    clusterArmId: (clusterName != 'null') ? cluster.id: null
  }
  tags: tags
}]

@description('The resource group the Azure Event Hub was deployed into.')
output resourceGroupName string = resourceGroup().name

@description('Azure Event Hub namespace details.')
output eventHubNamespaceDetails array = [for varEventHubNamespace in varEventHubNamespaces: {
  id: reference(varEventHubNamespace.eventHubNamespaceName,'2021-11-01','Full').resourceId
  serviceBusEndpoint: reference(varEventHubNamespace.eventHubNamespaceName,'2021-11-01','Full').properties.serviceBusEndpoint
  status: reference(varEventHubNamespace.eventHubNamespaceName,'2021-11-01','Full').properties.status
}]
```

```json
{
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
  "contentVersion": "1.0.0.0",
  "metadata": {
    "_generator": {
      "name": "bicep",
      "version": "0.16.2.56959",
      "templateHash": "8050482343911161743"
    }
  },
  "parameters": {
    "clusterName": {
      "type": "string",
      "defaultValue": "null",
      "metadata": {
        "description": "Optional. Name for the Event Hub cluster, Alphanumerics and hyphens characters, Start with letter, End with letter or number."
      }
    },
    "clusterCapacity": {
      "type": "int",
      "defaultValue": 1,
      "metadata": {
        "description": "Optional. The quantity of Event Hubs Cluster Capacity Units contained in this cluster."
      }
    },
    "location": {
      "type": "string",
      "defaultValue": "[resourceGroup().location]",
      "metadata": {
        "description": "Optional. Location for all resources."
      }
    },
    "tags": {
      "type": "object",
      "defaultValue": {},
      "metadata": {
        "description": "Optional. Tags of the resource."
      }
    },
    "eventHubNamespaces": {
      "type": "object",
      "defaultValue": {},
      "metadata": {
        "description": "Optional. The name of the event hub namespace to be created.\nBelow paramters you can pass while creating the Azure Event Hub namespace.\nsku: (Optional) Possible values are \"Basic\" or \"Standard\" or \"Premium\". Detault to 'Standard'.\ncapacity: (Optional) int, The Event Hubs throughput units for Basic or Standard tiers, where value should be 0 to 20 throughput units.The Event Hubs premium units for Premium tier, where value should be 0 to 10 premium units. Default to 1.\nzoneRedundant: (Optional) bool, Enabling this property creates a Standard Event Hubs Namespace in regions supported availability zones. Default to false.\nisAutoInflateEnabled: (Optional) bool,  Value that indicates whether AutoInflate is enabled for eventhub namespace. Only available for \"Standard\" sku. Default to false.\nmaximumThroughputUnits: (Optional) int, Upper limit of throughput units when AutoInflate is enabled, value should be within 0 to 20 throughput units. ( '0' if AutoInflateEnabled = true)\ndisableLocalAuth: (Optional) bool, This property disables SAS authentication for the Event Hubs namespace. Default to false.\nkafkaEnabled: (Optional) bool, Value that indicates whether Kafka is enabled for eventhub namespace. Default to true.\n"
      }
    }
  },
  "variables": {
    "copy": [
      {
        "name": "varEventHubNamespaces",
        "count": "[length(items(parameters('eventHubNamespaces')))]",
        "input": {
          "eventHubNamespaceName": "[items(parameters('eventHubNamespaces'))[copyIndex('varEventHubNamespaces')].key]",
          "sku": "[if(contains(items(parameters('eventHubNamespaces'))[copyIndex('varEventHubNamespaces')].value, 'sku'), items(parameters('eventHubNamespaces'))[copyIndex('varEventHubNamespaces')].value.sku, 'Standard')]",
          "capacity": "[if(contains(items(parameters('eventHubNamespaces'))[copyIndex('varEventHubNamespaces')].value, 'capacity'), items(parameters('eventHubNamespaces'))[copyIndex('varEventHubNamespaces')].value.capacity, 1)]",
          "zoneRedundant": "[if(contains(items(parameters('eventHubNamespaces'))[copyIndex('varEventHubNamespaces')].value, 'zoneRedundant'), items(parameters('eventHubNamespaces'))[copyIndex('varEventHubNamespaces')].value.zoneRedundant, false())]",
          "isAutoInflateEnabled": "[if(contains(items(parameters('eventHubNamespaces'))[copyIndex('varEventHubNamespaces')].value, 'isAutoInflateEnabled'), items(parameters('eventHubNamespaces'))[copyIndex('varEventHubNamespaces')].value.isAutoInflateEnabled, false())]",
          "maximumThroughputUnits": "[if(contains(items(parameters('eventHubNamespaces'))[copyIndex('varEventHubNamespaces')].value, 'maximumThroughputUnits'), items(parameters('eventHubNamespaces'))[copyIndex('varEventHubNamespaces')].value.maximumThroughputUnits, 0)]",
          "disableLocalAuth": "[if(contains(items(parameters('eventHubNamespaces'))[copyIndex('varEventHubNamespaces')].value, 'disableLocalAuth'), items(parameters('eventHubNamespaces'))[copyIndex('varEventHubNamespaces')].value.disableLocalAuth, false())]",
          "kafkaEnabled": "[if(contains(items(parameters('eventHubNamespaces'))[copyIndex('varEventHubNamespaces')].value, 'kafkaEnabled'), items(parameters('eventHubNamespaces'))[copyIndex('varEventHubNamespaces')].value.kafkaEnabled, true())]"
        }
      }
    ]
  },
  "resources": [
    {
      "condition": "[not(equals(parameters('clusterName'), 'null'))]",
      "type": "Microsoft.EventHub/clusters",
      "apiVersion": "2021-11-01",
      "name": "[parameters('clusterName')]",
      "location": "[parameters('location')]",
      "tags": "[parameters('tags')]",
      "sku": {
        "name": "Dedicated",
        "capacity": "[parameters('clusterCapacity')]"
      },
      "properties": {}
    },
    {
      "copy": {
        "name": "eventHubNamespace",
        "count": "[length(variables('varEventHubNamespaces'))]"
      },
      "condition": "[not(empty(parameters('eventHubNamespaces')))]",
      "type": "Microsoft.EventHub/namespaces",
      "apiVersion": "2021-11-01",
      "name": "[variables('varEventHubNamespaces')[copyIndex()].eventHubNamespaceName]",
      "location": "[parameters('location')]",
      "sku": {
        "name": "[variables('varEventHubNamespaces')[copyIndex()].sku]",
        "tier": "[variables('varEventHubNamespaces')[copyIndex()].sku]",
        "capacity": "[variables('varEventHubNamespaces')[copyIndex()].capacity]"
      },
      "properties": {
        "disableLocalAuth": "[variables('varEventHubNamespaces')[copyIndex()].disableLocalAuth]",
        "kafkaEnabled": "[variables('varEventHubNamespaces')[copyIndex()].kafkaEnabled]",
        "isAutoInflateEnabled": "[variables('varEventHubNamespaces')[copyIndex()].isAutoInflateEnabled]",
        "maximumThroughputUnits": "[if(variables('varEventHubNamespaces')[copyIndex()].isAutoInflateEnabled, variables('varEventHubNamespaces')[copyIndex()].maximumThroughputUnits, 0)]",
        "zoneRedundant": "[variables('varEventHubNamespaces')[copyIndex()].zoneRedundant]",
        "clusterArmId": "[if(not(equals(parameters('clusterName'), 'null')), resourceId('Microsoft.EventHub/clusters', parameters('clusterName')), null())]"
      },
      "tags": "[parameters('tags')]",
      "dependsOn": [
        "[resourceId('Microsoft.EventHub/clusters', parameters('clusterName'))]"
      ]
    }
  ],
  "outputs": {
    "resourceGroupName": {
      "type": "string",
      "metadata": {
        "description": "The resource group the Azure Event Hub was deployed into."
      },
      "value": "[resourceGroup().name]"
    },
    "eventHubNamespaceDetails": {
      "type": "array",
      "metadata": {
        "description": "Azure Event Hub namespace details."
      },
      "copy": {
        "count": "[length(variables('varEventHubNamespaces'))]",
        "input": {
          "id": "[reference(variables('varEventHubNamespaces')[copyIndex()].eventHubNamespaceName, '2021-11-01', 'Full').resourceId]",
          "serviceBusEndpoint": "[reference(variables('varEventHubNamespaces')[copyIndex()].eventHubNamespaceName, '2021-11-01', 'Full').properties.serviceBusEndpoint]",
          "status": "[reference(variables('varEventHubNamespaces')[copyIndex()].eventHubNamespaceName, '2021-11-01', 'Full').properties.status]"
        }
      }
    }
  }
}
```