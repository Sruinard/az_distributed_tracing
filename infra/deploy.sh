#!/bin/bash

# Create resource groups for 'API team' and 'App team' + deploy respective resources
az group create --name srtrace --location westeurope
# az group create --name prod-tripplanner --location westeurope

# CHECK: 'uniqueness' - make this unique for your local
az deployment group create --resource-group srtrace --template-file './infra/apiworkload.bicep' --parameters uniqueness=srtrace environment=dev
# az deployment group create --resource-group prod-tripplanner --template-file './infra/apiworkload.bicep' --parameters uniqueness=sruinard environment=prod --mode Complete