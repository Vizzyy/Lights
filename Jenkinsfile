#! groovy

String serviceName = "lights"
currentBuild.displayName = "$serviceName [$currentBuild.number]"

String commitHash = ""
Boolean deploymentCheckpoint = false
String startCommand = """
    cd ~/Lights
    git stash; git checkout master 
    git pull origin master
    sudo systemctl restart lights 
"""

try {
    if (ISSUE_NUMBER)
        echo "Building from pull request..."
} catch (Exception ignored) {
    ISSUE_NUMBER = false
    echo "Building from jenkins job..."
}

boolean confirmDeployed() {

    Boolean deployed1 = false
    Boolean deployed2 = false
    for (int i = 0; i < 5; i++) {

        try {
            def health = sh(
                    script: "curl http://herbivore:5000/outside/arrange/rainbowCycle",
                    returnStdout: true
            ).trim()
            echo health
            if (health.toString().contains("<h1>Indoor Lights!</h1><p>clear</p>")) {
                deployed1 = true
                break
            }
        } catch (Exception e) {
            echo "Could not parse health check response."
            e.printStackTrace()
        }

        sleep time: i, unit: 'SECONDS'

    }

    if (!deployed1)
        return false

    for (int i = 0; i < 5; i++) {

        try {
            def health = sh(
                    script: "curl http://carnivore:5000/inside/arrange/rainbowCycle",
                    returnStdout: true
            ).trim()
            echo health
            if (health.toString().contains("<h1>Indoor Lights!</h1><p>clear</p>")) {
                deployed2 = true
                break
            }
        } catch (Exception e) {
            echo "Could not parse health check response."
            echo """$e"""
            e.printStackTrace()
        }

        sleep time: i, unit: 'SECONDS'

    }

    return deployed1 && deployed2
}


pipeline {
    agent any
    options {
        buildDiscarder(logRotator(numToKeepStr:'10'))
        disableConcurrentBuilds()
        quietPeriod(1)
    }
    parameters {
        booleanParam(name: 'Build', defaultValue: true, description: 'Build latest artifact')
        booleanParam(name: 'Deploy', defaultValue: true, description: 'Deploy latest artifact')
    }
    stages {
        stage("Acknowledge") {
            steps {
                script {
                    if (env.Build == "true" && ISSUE_NUMBER) {
                        prTools.comment(ISSUE_NUMBER,
                                """{
                                    "body": "Jenkins triggered $currentBuild.displayName"
                                }""",
                                serviceName)
                    }
                }
            }
        }

        stage("Start") {
            steps {
                script {
                    if (env.Deploy == "true") {
                        deploymentCheckpoint = true;
                        sh("ssh pi@carnivore.local '$startCommand'")
                        sh("ssh pi@herbivore.local '$startCommand'")


                    }
                }
            }
        }

        stage("Confirm") {
            steps {
                script {

                    if (!confirmDeployed())
                        error("Failed to deploy.")

                    sh("ssh pi@carnivore.local 'sudo systemctl status lights'")
                    sh("ssh pi@herbivore.local 'sudo systemctl status lights'")
                }
            }
        }
    }
    post {
        success {
            script {
                if (env.Build == "true" && ISSUE_NUMBER) {
                    prTools.merge(ISSUE_NUMBER,
                            """{
                                "commit_title": "Jenkins merged $currentBuild.displayName",
                                "merge_method": "merge"
                            }""",
                            serviceName)
                    prTools.comment(ISSUE_NUMBER,
                            """{
                                "body": "Jenkins successfully deployed $currentBuild.displayName"
                            }""",
                            serviceName)
                }
                sh "echo '${env.GIT_COMMIT}' > ~/userContent/$serviceName-last-success-hash.txt"
            }
        }
        failure {
            script {
                if (env.Build == "true" && ISSUE_NUMBER) {
                    prTools.comment(ISSUE_NUMBER,
                            """{
                                "body": "Jenkins failed during $currentBuild.displayName"
                            }""",
                            serviceName)
                }
                if(deploymentCheckpoint) { // don't restart instance on failure if no deployment occured
                    commitHash = sh(script: "cat ~/userContent/$serviceName-last-success-hash.txt", returnStdout: true)
                    echo "Rolling back to previous successful image. Hash: $commitHash"
                    GString cmd = """
                        cd ~/Lights
                        git stash
                        git fetch --all
                        git checkout $commitHash 
                        sudo systemctl restart lights 
                    """
                    sh("ssh pi@carnivore.local '$cmd'")
                    sh("ssh pi@herbivore.local '$cmd'")
                    if (!confirmDeployed())
                        error("Failed to deploy.")
                    sh("ssh pi@carnivore.local 'sudo systemctl status lights'")
                    sh("ssh pi@herbivore.local 'sudo systemctl status lights'")
                }
            }
        }
        cleanup { // Cleanup post-flow always executes last
            deleteDir()
        }
    }
}