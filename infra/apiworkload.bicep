param uniqueness string = 'z9pqqf'
param environment string = 'dev'
var location = resourceGroup().location


resource appserviceplan 'Microsoft.Web/serverfarms@2021-01-15' = {
  name: '${environment}-${uniqueness}'
  location: location
  kind: 'linux'
  properties: {
    reserved: true
  }
  sku: {
     name: 'P1v2'
     tier: 'PremiumV2'
  }  
}

resource workspace 'Microsoft.OperationalInsights/workspaces@2021-06-01' = {
  name: '${environment}-${uniqueness}'
  location: location
}

resource appinsights 'Microsoft.Insights/components@2020-02-02' = {
  name: '${environment}-${uniqueness}'
  location: location
  kind: 'web'  
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: workspace.id    
  }
}


// ####################
// #####  COSMOS  #####
// ####################

resource cosmos_account 'Microsoft.DocumentDB/databaseAccounts@2021-07-01-preview' = {
  name: '${environment}-${uniqueness}'
  location: location
  properties: {
    createMode: 'Default'
    databaseAccountOfferType: 'Standard'
    locations: [
      {
        'locationName': location
        'failoverPriority': 0
        'isZoneRedundant':false
      }
    ]
  }
}

resource cosmos_db 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases@2021-04-15' = {
  name: '${cosmos_account.name}/webshop'
  location: location
  properties: {
    resource: {
      id: 'webshop'
    }
    options: {
      throughput: 400
    }
  }
}

resource cosmosdb_container 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2021-06-15' = {
  name: '${cosmos_db.name}/orders'
  location: location
  properties: {
    resource: {
      id: 'orders'
      partitionKey:{
        kind: 'Hash'
        paths: [
          '/item_id'
        ]
        version: 1
      }
    }
  }
}

resource redis 'Microsoft.Cache/redis@2020-12-01' = {
  name: '${environment}-${uniqueness}'
  location: location
  properties: {
    redisVersion: '6.0.14'
    sku: {
      name: 'Standard'
      family: 'C'
      capacity: 1
    }
  }
}


resource webshop 'Microsoft.Web/sites@2021-02-01' = {
  name: '${uniqueness}-webshop'
  location: 'westeurope'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    serverFarmId: appserviceplan.id
    httpsOnly: true    
    siteConfig: {
      cors: {
        allowedOrigins: [
          '*'
        ]
        supportCredentials: false
      }
      appSettings: [
        {
          name: 'APPINSIGHTS_INSTRUMENTATIONKEY'
          value: appinsights.properties.InstrumentationKey
        }
        {
          name: 'APPINSIGHTS_CONNECTION_STRING'
          value: appinsights.properties.ConnectionString
        }
        {
          name: 'REDIS_HOST'
          value: redis.properties.hostName
        }
        {
          name: 'REDIS_PASS'
          value: listKeys(redis.id, redis.apiVersion).PrimaryKey
        }
        {
          name: 'REDIS_PORT'
          value: string(redis.properties.sslPort)
        }
        {
          name: 'PAYMENTS_ENDPOINT'
          value: 'https://${payments.properties.defaultHostName}/'
        }
        {
          name: 'SHIPMENTS_ENDPOINT'
          value: 'https://${shipping.properties.defaultHostName}/'
        }
        {
          name: 'ApplicationInsightsAgent_EXTENSION_VERSION'
          value: '~3'
        }
        {
          name: 'XDT_MicrosoftApplicationInsights_Mode'
          value: 'recommended'
        }
      ]
      
      linuxFxVersion: 'python|3.7'
      alwaysOn: false
      
    }
    clientAffinityEnabled: false    
  }  
}

resource payments 'Microsoft.Web/sites@2021-02-01' = {
  name: '${uniqueness}-payments'
  location: 'westeurope'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    serverFarmId: appserviceplan.id
    httpsOnly: true    
    siteConfig: {
      cors: {
        allowedOrigins: [
          '*'
        ]
        supportCredentials: false
      }
      appSettings: [
        {
          name: 'APPINSIGHTS_INSTRUMENTATIONKEY'
          value: appinsights.properties.InstrumentationKey
        }
        {
          name: 'APPINSIGHTS_CONNECTION_STRING'
          value: appinsights.properties.ConnectionString
        }
        {
          name: 'SHIPPING_ENDPOINT'
          value: 'https://${shipping.properties.defaultHostName}/'
        }
        {
          name: 'ApplicationInsightsAgent_EXTENSION_VERSION'
          value: '~3'
        }
        {
          name: 'XDT_MicrosoftApplicationInsights_Mode'
          value: 'recommended'
        }
      ]
      
      linuxFxVersion: 'python|3.7'
      alwaysOn: false
      
    }
    clientAffinityEnabled: false    
  }  
}

resource shipping 'Microsoft.Web/sites@2021-02-01' = {
  name: '${uniqueness}-shipping'
  location: 'westeurope'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    serverFarmId: appserviceplan.id
    httpsOnly: true    
    siteConfig: {
      cors: {
        allowedOrigins: [
          '*'
        ]
        supportCredentials: false
      }
      appSettings: [
        {
          name: 'APPINSIGHTS_INSTRUMENTATIONKEY'
          value: appinsights.properties.InstrumentationKey
        }
        {
          name: 'APPINSIGHTS_CONNECTION_STRING'
          value: appinsights.properties.ConnectionString
        }
        {
          name: 'ACCOUNT_URI'
          value: cosmos_account.properties.documentEndpoint
        }        
        {
          name: 'ACCOUNT_KEY'
          value: listKeys(cosmos_account.id, cosmos_account.apiVersion).primaryMasterKey
        }     
        {
          name: 'ApplicationInsightsAgent_EXTENSION_VERSION'
          value: '~3'
        }
        {
          name: 'XDT_MicrosoftApplicationInsights_Mode'
          value: 'recommended'
        }
      ]
      
      linuxFxVersion: 'python|3.7'
      alwaysOn: false
      
    }
    clientAffinityEnabled: false    
  }  
}
















