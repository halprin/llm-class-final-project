terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
      version = "6.14.1"
    }
  }

  backend "s3" {
    bucket         = "halprin-a6556ebde1574d01a40c8d1f7747a234-terraform-state"
    key            = "llm-class-final-project.tfstate"
    region         = "us-east-1"
  }
}

provider "aws" {
  region = "us-east-1"

  default_tags {
    project = "halprin-llm-class-final-project"
  }
}
