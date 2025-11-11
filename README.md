# ACEest_Fitness
Assignment2 -- DevOps CI/CD implementation for ACEest Fitness &amp; Gym

This repository hosts the ACEest Fitness Management System, a foundational Flask web application, and implements an enterprise-grade Continuous Integration and Continuous Delivery (CI/CD) pipeline using Jenkins, SonarQube, Docker, and Kubernetes.

This project was developed to demonstrate best practices across the full software development lifecycle, from unit testing and static analysis to advanced Kubernetes deployment methodologies.

🚀 Key Features and Deliverables

This project successfully implements the following core components:

Foundational Web Application (Flask):

Developed using Pythonic standards with modular, maintainable code (ACEest_Fitness.py serves as the core).

The application is containerized using Docker and published to Docker Hub.

Continuous Integration (CI):

Jenkins: Configured as the central CI build server, polling the Git repository for automatic builds upon code changes.

Unit Testing: Comprehensive unit tests are implemented using Pytest and are automatically executed during the CI pipeline.

Static Analysis (SonarQube): Integrated for static code analysis, ensuring code quality and enforcing Quality Gate standards before build promotion.

Continuous Delivery/Deployment (CD):

Containerization: The application is packaged into a self-contained, version-controlled Docker image.

Kubernetes (K8s): Deployment is managed via Kubernetes (designed for Minikube/local clusters or cloud integration). All Kubernetes deployment manifests are located in the dedicated deployment/ directory.

Advanced Deployment Strategies:

The Kubernetes configuration supports various advanced deployment patterns to ensure high availability and safe rollouts:

Rolling Updates

Blue-Green Deployment (via service/selector manipulation)

Canary Release

Shadow Deployment

A/B Testing

🗺️ Project Structure

The repository adheres to the following structure:

ACEest_Fitness_System/
├── src/app.py       # Main Flask application file
├── requirements.txt        # Python dependencies
├── Dockerfile              # Containerization instructions
├── tests/                  # Pytest unit tests
│   └── test_app.py
├── deployment/             # All Kubernetes YAML Manifests
│   ├── k8s-deployment.yaml # Base Deployment and Service
│   ├── k8s-blue-green.yaml # Manifests for Blue/Green strategy
│   └── k8s-canary.yaml     # Manifests for Canary strategy
├── Jenkinsfile             # Declarative Pipeline for Jenkins CI/CD
└── README.md


⚙️ Local Setup and Prerequisites

To replicate the CI/CD environment and deployment locally, ensure the following tools are installed and configured:

Component

Purpose

Local Access URL (Default)

Git

Version Control

N/A

Python 3.x

Application Development

N/A

Docker (or Podman)

Containerization

N/A

Minikube

Local Kubernetes Cluster

N/A

Jenkins

Continuous Integration Server

http://localhost:8080

SonarQube

Static Code Analysis

http://localhost:9000

CI/CD Service Configuration

Both Jenkins and SonarQube are configured to run on their default local host ports:

Jenkins: Access the Jenkins dashboard at http://localhost:8080. The pipeline is configured to use the Jenkinsfile for the build, test, analysis, and deployment process.

SonarQube: Access the SonarQube dashboard at http://localhost:9000. The Jenkins pipeline integrates with SonarQube to perform static analysis and quality gate checks on the code before the Docker image is built.

Kubernetes Deployment Artifacts

All necessary YAML files for deployment are placed under the deployment/ directory. These files are designed to target a local Kubernetes cluster (like Minikube) and can be applied using kubectl.

# Example: Deploying the base application
kubectl apply -f deployment/flask-app-deployment.yaml

# Example: Checking the deployed services
minikube service aceessfitness-service --url


📐 CI/CD Pipeline Overview

The pipeline executes a strict workflow defined in the Jenkinsfile:

Checkout: Fetch the latest code from the Git repository.

Testing (Pytest): Run unit tests. (Failure halts pipeline)

Code Analysis (SonarQube): Run static analysis. Wait for Quality Gate status. (Failure halts pipeline)

Build: Build the new Docker image (docker build . -t <user>/aceest-fitness:<version>).

Push: Push the versioned image to Docker Hub.

Deployment (Kubernetes): Apply the necessary Kubernetes manifest from the deployment/ folder to deploy the new version.

✅ Running Unit Tests

To run the Pytest suite locally before committing, use the following commands:

# Install dependencies
pip install -r requirements.txt
pip install pytest

# Run the tests
pytest


🛠️ Advanced Deployment Strategy Details

The project includes artifacts and documentation to support the following advanced deployment mechanisms:

Strategy

Description

Key Mechanism

Rollback

Rolling Update

Gradual replacement of old pod instances with new ones.

Default strategy: RollingUpdate in Deployment object.

Automated via kubectl rollout undo.

Blue-Green

Two identical production environments (blue and green) are run. Traffic is switched instantly via the Service selector.

Two separate Deployments, one Service targeting the active version.

Change Service selector back to the old stable version.

Canary Release

A small percentage of traffic is routed to the new version before a full rollout.

Three Deployments (Old, New/Canary), and an Ingress/Load Balancer to split traffic by weight.

Delete the Canary Deployment.

Shadow Deployment

New version receives production traffic copies (mirroring) but the response is ignored, allowing for load testing without affecting users.

Service mesh or proxy configuration to mirror traffic to the "shadow" Deployment.

Stop mirroring traffic and delete the Shadow Deployment.
