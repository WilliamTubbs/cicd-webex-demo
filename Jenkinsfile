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
          # install deps (quietly to avoid thread issues)
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
    // Use Python's stdlib to POST JSON (no curl, no extra packages)
    // Run on the controller node; no Docker/apt needed.
    withEnv(["WEBEX_TEXT=${msg.replace('\"','\\\\\"')}"]) {
      sh '''
        python - <<'PY'
import os, json, urllib.request
token = os.environ['WEBEX_TOKEN']
room  = os.environ['WEBEX_ROOM']
text  = os.environ['WEBEX_TEXT']
data  = json.dumps({"roomId": room, "markdown": text}).encode()
req   = urllib.request.Request(
  "https://webexapis.com/v1/messages",
  data=data,
  headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
)
with urllib.request.urlopen(req) as r:
    print("Webex status:", r.status)
PY
      '''
    }
  }
}
