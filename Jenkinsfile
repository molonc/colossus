node {

    try {
        stage 'Checkout'
            checkout scm

            sh 'git log HEAD^..HEAD --pretty="%h %an - %s" > GIT_CHANGES'
            def lastChanges = readFile('GIT_CHANGES')
            slackSend color: "warning", message: "Started `${env.JOB_NAME}#${env.BUILD_NUMBER}`\n\n_The changes:_\n${lastChanges}"

        stage 'Test'
            slackSend color: "warning", message: "Started Testing `${env.JOB_NAME}#${env.BUILD_NUMBER}`"
            sh "ssh ubuntu@$ColossusTestVM bash -e /home/ubuntu/colossus/test/test_colossus.sh"
            slackSend color: "warning", message: "Finished Testing `${env.JOB_NAME}#${env.BUILD_NUMBER}`"

        stage 'Deploy'
            sh "ssh ubuntu@$ColossusVM_IP bash -e /home/ubuntu/colossus/deployment/deploy_production_colossus.sh"

        stage 'Publish results'
            slackSend color: "good", message: "Congrats! Build successful: `${env.JOB_NAME}#${env.BUILD_NUMBER}` <${env.BUILD_URL}|Open in Jenkins>"
    }

    catch (err) {
        slackSend color: "danger", message: "Error! Build failed :face_with_head_bandage: \n`${env.JOB_NAME}#${env.BUILD_NUMBER}` <${env.BUILD_URL}|Open in Jenkins>"

        throw err
    }

}