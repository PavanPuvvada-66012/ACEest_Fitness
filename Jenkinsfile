// This Jenkinsfile must be placed in the root directory of your Git repository.
// It uses a Declarative Pipeline syntax, optimized for a Python project.

pipeline {
    // Agent: Use a Docker image to ensure a consistent Python environment for the build.
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
                // Create and activate a virtual environment
                sh 'python -m venv ${VENV_DIR}'
                sh '. ${VENV_DIR}/bin/activate && pip install --upgrade pip'
                // Install project dependencies from requirements.txt
                sh '. ${VENV_DIR}/bin/activate && pip install -r requirements.txt'
            }
        }

        stage('Lint and Quality Check') {
            steps {
                echo 'Running static analysis (e.g., flake8 or black)...'
                // Assuming 'flake8' is included in your requirements.txt
                sh '. ${VENV_DIR}/bin/activate && flake8 --max-line-length=120 --exclude=./${VENV_DIR},.git'
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
                // For web apps: sh 'ansible-playbook deploy.yml' or 'kubectl apply -f deployment.yaml'
                // For libraries: sh '. ${VENV_DIR}/bin/activate && python setup.py sdist bdist_wheel'
                // sh '. ${VENV_DIR}/bin/activate && twine upload dist/*'
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
