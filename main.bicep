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
