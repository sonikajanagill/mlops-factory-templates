terraform {
  required_version = ">= 1.5"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 5.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = ">= 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
}

# 1. Project Setup (APIs)
module "project_setup" {
  source     = "./modules/project-setup"
  project_id = var.project_id
}

# 2. IAM & Service Accounts
module "iam" {
  source     = "./modules/iam"
  project_id = var.project_id
  depends_on = [module.project_setup]
}

# 3. Storage Buckets
module "storage" {
  source     = "./modules/storage"
  project_id = var.project_id
  region     = var.region
  depends_on = [module.project_setup]
}

# 4. Cloud Composer (Orchestration)
module "composer" {
  source          = "./modules/composer"
  project_id      = var.project_id
  region          = var.region
  composer_name   = "mlops-factory-composer"
  network_name    = "default" # Using default for simplicity, prod should use custom VPC
  service_account = module.iam.sa_composer_email
  depends_on      = [module.iam, module.storage]
}

# 5. Vertex AI (Pipelines, Feature Store, Registry)
module "vertex_ai" {
  source          = "./modules/vertex-ai"
  project_id      = var.project_id
  region          = var.region
  service_account = module.iam.sa_vertex_pipeline_email
  depends_on      = [module.iam, module.storage]
}

# 6. Monitoring
module "monitoring" {
  source     = "./modules/monitoring"
  project_id = var.project_id
  depends_on = [module.project_setup]
}
