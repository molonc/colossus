pipeline {
    agent any
    stages {
        stage('Checkout'){
            steps{
                checkout scm
                sh 'git log HEAD^..HEAD --pretty="%h %an - %s" > GIT_CHANGES'
                def lastChanges = readFile('GIT_CHANGES')
                slackSend color: "warning", message: "Started `${env.JOB_NAME}#${env.BUILD_NUMBER}`\n\n_The changes:_\n${lastChanges}"
            }
        }
    }
}