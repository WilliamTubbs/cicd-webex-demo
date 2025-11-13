pipeline {
  agent { docker { image 'python:3.11-slim'; args '-u root' } }

  options { timestamps(); ansiColor('xterm') }

  stages {
    stage('Checkout') {
      steps {
        // use the Pipeline job's SCM config (no hardcoded URL here)
        checkout scm
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
    success { script { sendWebex("Build SUCCESS: ${env.JOB_NAME} #${env.BUILD_NUMBER}") } }
    failure { script { sendWebex("Build FAILED: ${env.JOB_NAME} #${env.BUILD_NUMBER}") } }
  }
}

def sendWebex(String text) {
  withCredentials([
    string(credentialsId: 'webex-bot-token', variable: 'WEBEX_TOKEN'),
    string(credentialsId: 'webex-room-id',  variable: 'WEBEX_ROOM')
  ]) {
    sh """
      curl -s -X POST 'https://webexapis.com/v1/messages' \
        -H 'Authorization: Bearer ${WEBEX_TOKEN}' \
        -H 'Content-Type: application/json' \
        -d '{"roomId": "'${WEBEX_ROOM}'", "markdown": "'${text.replace("\"","\\\"")}'"}'
    """
  }
}

