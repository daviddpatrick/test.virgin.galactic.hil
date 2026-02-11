pipeline {
    agent any
    options {
        timestamps()
    }
    environment {
        PIP_DISABLE_PIP_VERSION_CHECK = '1'
        PYTHONDONTWRITEBYTECODE = '1'
    }
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        stage('Setup venv') {
            steps {
                sh 'python3 -m venv .venv'
            }
        }
        stage('Install deps') {
            steps {
                sh '. .venv/bin/activate && pip install -r requirements.txt'
            }
        }
        stage('Run tests') {
            steps {
                sh 'rm -rf allure-results && mkdir -p allure-results'
                sh '. .venv/bin/activate && pytest -v'
            }
        }
    }
    post {
        always {
            archiveArtifacts artifacts: 'allure-results/**', allowEmptyArchive: true
            allure includeProperties: false, jdk: '', results: [[path: 'allure-results']]
        }
    }
}
