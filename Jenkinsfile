node {

    try {
        stage 'Checkout'
            checkout scm

            sh 'git log HEAD^..HEAD --pretty="%h %an - %s" > GIT_CHANGES'
            def lastChanges = readFile('GIT_CHANGES')
            slackSend color: "warning", message: "Started `${env.JOB_NAME}#${env.BUILD_NUMBER}`\n\n_The changes:_\n${lastChanges}"

        stage 'Test'
            slackSend color: "warning", message: "Started Testing `${env.JOB_NAME}#${env.BUILD_NUMBER}`"
            sh "az login --service-principal --username $CLIENT_ID --password $SECRET_KEY --tenant $TENANT_ID"
	    sh "az vm start -g olympus -n colossus-test" 
	    sh "ssh ubuntu@$ColossusTestVM bash -e /home/ubuntu/colossus/test/test_colossus.sh"
	    sh "az vm stop -g olympus -n colossus-test"
            slackSend color: "warning", message: "Finished Testing `${env.JOB_NAME}#${env.BUILD_NUMBER}` and Test Server Deallocated"

        stage 'Publish results'
            slackSend color: "good", message: "Congrats! Build successful: `${env.JOB_NAME}#${env.BUILD_NUMBER}` <${env.BUILD_URL}|Open in Jenkins>"
    }

    catch (err) {
        slackSend color: "danger", message: "Error! Build failed :face_with_head_bandage: \n`${env.JOB_NAME}#${env.BUILD_NUMBER}` <${env.BUILD_URL}|Open in Jenkins>"

        throw err
    }

}
