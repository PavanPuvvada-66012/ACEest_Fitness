// This Jenkinsfile must be placed in the root directory of your Git repository.
// It uses a Declarative Pipeline syntax, optimized for a Python project.

pipeline {
    // Removed the failing 'tools' directive and the 'docker' agent.
    agent any

    // Environment variables can define key parameters like the virtual environment path
    environment {
        // Defines the name of the virtual environment directory
        VENV_DIR = '.venv'
    }

    // Triggers: Defines how the pipeline should be started.
    triggers {
        // SCM polling ensures a check for changes at regular intervals.
        // The actual schedule is configured in the Jenkins Job UI.
        pollSCM('')
    }

    // Stages: The main steps of your CI/CD process.
    stages {
        stage('Checkout Code') {
            steps {
                echo 'Checking out code from the repository...'
                script {
                    checkout scm
                }
            }
        }

        stage('Install Dependencies') {
            steps {
                echo 'Setting up Python virtual environment and installing dependencies...'
                // FIX: Changed 'python' to 'python3' as this is often the correct executable name.
                // If this fails again, you will need to replace 'python3' with the absolute path
                // of the Python executable on your Jenkins build agent (e.g., /usr/bin/python3).
                sh 'python3 -m venv ${VENV_DIR}'
                sh '. ${VENV_DIR}/bin/activate && pip install --upgrade pip'
                // Install project dependencies from requirements.txt
                sh '. ${VENV_DIR}/bin/activate && pip install -r requirements.txt'
            }
        }

        stage('Lint and Quality Check') {
            steps {
                echo 'Running static analysis using Pylint...'
                sh '. ${VENV_DIR}/bin/activate && pylint **/*.py || true' 
            }
        }

        stage('Run Tests') {
            steps {
                echo 'Executing unit and integration tests (e.g., pytest)...'
                // Assuming 'pytest' is included in your requirements.txt
                sh '. ${VENV_DIR}/bin/activate && pytest'
            }
        }

        stage('Deploy (main branch only)') {
            // When: Only execute this stage if the current branch is 'main'
            when {
                branch 'main'
            }
            steps {
                echo "Deploying the built Python application or library..."
                // Placeholder for deployment commands:
                // Ensure activation is used for deployment steps that require VENV tools
                sh '. ${VENV_DIR}/bin/activate && echo "Running deployment script..."'
                // Example: sh '. ${VENV_DIR}/bin/activate && ansible-playbook deploy.yml'
            }
        }
    }

    // Post: Actions that run after the Pipeline has finished.
    post {
        always {
            echo 'Pipeline job finished.'
        }
        success {
            echo 'Python Build, Quality Check, and Tests succeeded!'
            // Add notification logic
        }
        failure {
            echo 'Python Build failed! Review the logs.'
            // Add notification logic
        }
    }
}
