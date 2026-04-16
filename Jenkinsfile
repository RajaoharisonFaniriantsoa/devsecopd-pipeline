pipeline {
  agent any

  environment {
    HARBOR_REGISTRY = "192.168.88.128"
    IMAGE_NAME      = "myproject/fastapi-app"
    IMAGE_TAG       = "${env.BUILD_NUMBER}"
    HARBOR_CREDS    = credentials('harbor-credentials')
  }

  stages {

    stage('Stage 1 — SAST & Secrets Scan') {
  steps {
    sh 'pip3 install bandit --quiet'
    sh '/var/lib/jenkins/.local/bin/bandit -r src/ -f json -o bandit-report.json || true'
    sh 'gitleaks detect --source=. --report-format json --report-path gitleaks-report.json || true'
  }
  post {
    always { archiveArtifacts artifacts: '*-report.json', allowEmptyArchive: true }
  }
}

    stage('Stage 2 — Docker Build') {
      steps {
        sh "docker build -t ${HARBOR_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG} -f docker/Dockerfile ."
      }
    }

    stage('Stage 3 — Container Scan') {
  steps {
    sh """
      trivy image \
        --exit-code 0 \
        --severity HIGH,CRITICAL \
        --format json \
        --output trivy-report.json \
        ${HARBOR_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}
    """
  }
  post {
    always { archiveArtifacts artifacts: 'trivy-report.json', allowEmptyArchive: true }
  }
}

    stage('Stage 4 — Push to Harbor') {
  steps {
    sh """
      echo \$HARBOR_CREDS_PSW | docker login ${HARBOR_REGISTRY} \
        -u \$HARBOR_CREDS_USR --password-stdin
      docker push ${HARBOR_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}
    """
  }
}

stage('Stage 5 — Sign Image') {
  environment {
    COSIGN_PASSWORD = credentials('cosign-password')
  }
  steps {
    sh """
      COSIGN_INSECURE_REGISTRY=true \
      COSIGN_PASSWORD=\$COSIGN_PASSWORD \
      cosign sign --yes \
        --key /var/lib/jenkins/cosign_keys/cosign.key \
        ${HARBOR_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}
    """
  }
}

    stage('Stage 6 — Harbor Scan Policy Check') {
      steps {
        sh """
          echo "Waiting for Harbor Trivy scan to complete..."
          sleep 30
          RESULT=\$(curl -s -u \$HARBOR_CREDS_USR:\$HARBOR_CREDS_PSW \
            http://${HARBOR_REGISTRY}/api/v2.0/projects/myproject/repositories/fastapi-app/artifacts/${IMAGE_TAG} \
            | python3 -c "
import sys, json
data = json.load(sys.stdin)
overview = data.get('scan_overview', {})
for k, v in overview.items():
    print(v.get('scan_status', 'unknown'))
")
          echo "Harbor scan status: \$RESULT"
        """
      }
    }

    stage('Stage 7 — Deploy') {
      steps {
        sh """
          export IMAGE=${HARBOR_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}
          docker compose -f docker-compose.yml up -d --pull always
        """
      }
    }
  }

  post {
    success {
      echo "Pipeline completed successfully. Image: ${HARBOR_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
    }
    failure {
      echo "Pipeline failed. Check the logs above."
    }
  }
}
