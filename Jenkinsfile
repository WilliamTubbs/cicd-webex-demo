pipeline {
  agent { docker { image 'python:3.11-slim'; args '-u root' } }
  options { timestamps(); ansiColor('xterm') }

  stages {
    stage('Checkout') {
      steps { checkout scm }
    }

    stage('Install') {
      steps {
        sh '''
          set -e
          python -V

          # Work around apt post-invoke hook issue in slim images
          rm -f /etc/apt/apt.conf.d/docker-clean || true
          apt-get update -o APT::Update::Post-Invoke-Success::= -o APT::Update::Post-Invoke::= -y
          apt-get install -y --no-install-recommends curl ca-certificates
          rm -rf /var/lib/apt/lists/*

          # Quieter pip to avoid thread issues on small VMs
          pip install --no-cache-dir --progress-bar off -r requirements.txt
        '''
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

def sendWebex(String msg) {
  withCredentials([
    string(credentialsId: 'webex-bot-token', variable: 'WEBEX_TOKEN'),
    string(credentialsId: 'webex-room-id',  variable: 'WEBEX_ROOM')
  ]) {
    // pass message via env; avoid Groovy interpolation of secrets
    withEnv(["WEBEX_TEXT=${msg.replace('\"','\\\\\"')}"]) {
      sh '''
        set -e
        curl -s -X POST "https://webexapis.com/v1/messages" \
          -H "Authorization: Bearer $WEBEX_TOKEN" \
          -H "Content-Type: application/json" \
          -d "{\"roomId\":\"$WEBEX_ROOM\",\"markdown\":\"$WEBEX_TEXT\"}" >/dev/null
      '''
    }
  }
}
