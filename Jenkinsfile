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
          # ensure curl exists for Webex notifications later
          apt-get update -y
          apt-get install -y --no-install-recommends curl ca-certificates
          rm -rf /var/lib/apt/lists/*

          # install deps with minimal overhead (avoid pip progress threads)
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

def sendWebex(String text) {
  withCredentials([
    string(credentialsId: 'webex-bot-token', variable: 'WEBEX_TOKEN'),
    string(credentialsId: 'webex-room-id',  variable: 'WEBEX_ROOM')
  ]) {
    // avoid Groovy interpolation of secrets: use shell vars ($WEBEX_TOKEN / $WEBEX_ROOM)
    sh '''
      set -e
      TEXT="$1"
      curl -s -X POST "https://webexapis.com/v1/messages" \
        -H "Authorization: Bearer $WEBEX_TOKEN" \
        -H "Content-Type: application/json" \
        -d "{\"roomId\":\"$WEBEX_ROOM\",\"markdown\":\"$TEXT\"}" >/dev/null
    ''' , arguments: [text]
  }
}
