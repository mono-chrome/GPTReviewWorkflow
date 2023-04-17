from review import call_gpt


STORAGE_BICEP_TEMPLATE = """
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
"""

BASIC_BICEP_TEMPLATE = """
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

"""

simplify_code_prompt = f"""
Can you propose ways to simplify this bicep code?

```bicep
{BASIC_BICEP_TEMPLATE}
```
"""

prompt = f"""
What are ways to simplify this bicep code?
- print the entire bicep file so I can copy the new contents into my existing file
```bicep
{BASIC_BICEP_TEMPLATE}
```
"""

system = {
    "role": "system",
    "content": """
    When reviewing the code remember:
    - Keep all @description annotations even when trying to make the code more concise.
    - One thing to look for is where `??` operator can be used instead of `contains()` to directly assigns default
    - removed unnecessary `if` conditions from resources loops
    """,
}
response = call_gpt(prompt, temperature=0.00, max_tokens=1200, system=system)
print(response)

if (
    "resource eventHubNamespace 'Microsoft.EventHub/namespaces@2021-11-01' = [for varEventHubNamespaces in varEventHubNamespaces : {"
    in response
):
    print("Correct!")
