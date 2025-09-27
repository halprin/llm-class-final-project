resource "aws_ecr_repository" "app" {
  name                 = "halprin-llm-class-final-app"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}
