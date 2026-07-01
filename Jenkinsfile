pipeline {
    agent any
    
    options {
        // Prevent Jenkins from doing an automatic checkout before the stages start
        skipDefaultCheckout()
    }
    
    environment {
        DOCKER_REGISTRY = "dh2uhf2i"
        IMAGE_NAME      = "myapp"
        BUILD_TAG       = "${BUILD_NUMBER}"
    }
    
    stages {
        stage('Checkout Code') {
            steps {
                // Now it's safe to clean the workspace because code hasn't been fetched yet
                cleanWs()
                checkout scm
            }
        }
        
        stage('Run Lint & Code Tests') {
            steps {
                echo 'Installing testing dependencies and running flake8 linting...'
                bat 'pip install flake8'
                // Replaced app.py with '.' to scan the workspace and prevent FileNotFoundError
                bat 'flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics'
            }
        }
        
        stage('Build Docker Image') {
            steps {
                echo 'Building the production Docker image...'
                bat "docker build -t ${IMAGE_NAME}:${BUILD_TAG} ."
                bat "docker tag ${IMAGE_NAME}:${BUILD_TAG} ${IMAGE_NAME}:latest"
            }
        }
        
        stage('Push to Registry') {
            steps {
                echo 'Logging into Docker Hub securely and pushing image...'
                withCredentials([usernamePassword(credentialsId: 'dh2uhf2i', passwordVariable: 'PASS', usernameVariable: 'USER')]) {
                    // Safe method for Windows agents: Write token to a temp file, feed to stdin, and immediately delete it
                    bat """
                        echo %PASS% > docker_pass.tmp
                        docker login -u %USER% --password-stdin < docker_pass.tmp
                        del docker_pass.tmp
                    """
                    bat "docker tag ${IMAGE_NAME}:${BUILD_TAG} ${DOCKER_REGISTRY}/${IMAGE_NAME}:${BUILD_TAG}"
                    bat "docker tag ${IMAGE_NAME}:${BUILD_TAG} ${DOCKER_REGISTRY}/${IMAGE_NAME}:latest"
                    bat "docker push ${DOCKER_REGISTRY}/${IMAGE_NAME}:${BUILD_TAG}"
                    bat "docker push ${DOCKER_REGISTRY}/${IMAGE_NAME}:latest"
                }
            }
        }
        
        stage('Deploy to Kubernetes') {
            steps {
                echo 'Applying secret and manifest updates securely to Kubernetes cluster...'
                withCredentials([file(credentialsId: 'kubeconfig-secret', variable: 'KUBECONFIG')]) {
                    bat "kubectl --kubeconfig=%KUBECONFIG% apply -f secret.yaml"
                    bat "kubectl --kubeconfig=%KUBECONFIG% apply -f deployment.yaml"
                    bat "kubectl --kubeconfig=%KUBECONFIG% rollout restart deployment/python-app"
                }
            }
        }
    }
    
    post {
        always {
            echo 'Cleaning up local Docker images from agent workspace...'
            bat "docker rmi ${IMAGE_NAME}:${BUILD_TAG} ${IMAGE_NAME}:latest ${DOCKER_REGISTRY}/${IMAGE_NAME}:${BUILD_TAG} ${DOCKER_REGISTRY}/${IMAGE_NAME}:latest || exit 0"
        }
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed. Review the step logs above.'
        }
    }
}
