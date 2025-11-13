pipeline {
  agent { docker { image 'python:3.11-slim'; args '-u root' } }

  environment {
    PIP_DISABLE_PIP_VERSION_CHECK = '1'
    PIP_NO_CACHE_DIR = '1'
  }

  options {
    timestamps()
    ansiColor('xterm')
  }

  triggers {
    // IMPORTANT: matches the GitHub webhook to /github-webhook/
    pollSCM('') // leave empty; actual trigger is the GitHub webhook checkbox in job config
  }

  stages {
    stage('Checkout') {
      steps {
        checkout([$class: 'GitSCM',
          userRemoteConfigs: [[url: 'https://github.com/WilliamTubbs/ci-cd-webex-demo']],
          branches: [[name: '*/main']]
        ])
      }
    }

    stage('Install') {
      steps {
        sh 'python -V'
        sh 'pip install -r requirements.txt'
      }
    }

    stage('Test') {
      steps {
        sh 'pytest -q --junitxml=report.xml'
      }
      post {
        always {
          junit 'report.xml'
          archiveArtifacts artifacts: 'report.xml', onlyIfSuccessful: false
        }
      }
    }
  }

  post {
    success {
      script {
        sendWebex("✅ Build SUCCESS on ${env.JOB_NAME} #${env.BUILD_NUMBER}")
      }
    }
    failure {
      script {
        sendWebex("❌ Build FAILED on ${env.JOB_NAME} #${env.BUILD_NUMBER}")
      }
    }
  }
}

def sendWebex(String text) {
  withCredentials([
    string(credentialsId: 'webex-bot-token', variable: 'WEBEX_TOKEN'),
    string(credentialsId: 'webex-room-id',  variable: 'WEBEX_ROOM')
  ]) {
    sh """
      curl -s -X POST 'https://webexapis.com/v1/messages' \\
        -H 'Authorization: Bearer ${WEBEX_TOKEN}' \\
        -H 'Content-Type: application/json' \\
        -d '{"roomId": "'${WEBEX_ROOM}'", "markdown": "'${text.replace("\"","\\\"")}'"}' \\
        | sed -e 's/\\\\n/ /g'
    """
  }
}
