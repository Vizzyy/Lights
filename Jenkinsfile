#! groovy

String serviceName = "lights"
currentBuild.displayName = "$serviceName [$currentBuild.number]"

String commitHash = ""
Boolean deploymentCheckpoint = false
String startCommand = """cd ~/Lights; \
git stash; git pull origin master; \
sudo systemctl restart lights; \
sudo systemctl status lights;"""

try {
    if (ISSUE_NUMBER)
        echo "Building from pull request..."
} catch (Exception ignored) {
    ISSUE_NUMBER = false
    echo "Building from jenkins job..."
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
                    if (env.Deploy == "true") {

                        Boolean deployed1 = false
                        Boolean deployed2 = false
                        for (int i = 0; i < 12; i++) {

                            try {
                                def health = sh(
                                        script: "curl http://herbivore:5000/outside/",
                                        returnStdout: true
                                ).trim()
                                echo health
                                if (health.toString().contains("<title id=\"title\">/outside</title>")) {
                                    deployed1 = true
                                    break
                                }
                            } catch (Exception e) {
                                echo "Could not parse health check response."
                                e.printStackTrace()
                            }

                            sleep time: i, unit: 'SECONDS'

                        }

                        for (int i = 0; i < 12; i++) {

                            try {
                                def health = sh(
                                        script: "curl http://carnivore:5000/inside/",
                                        returnStdout: true
                                ).trim()
                                echo health
                                if (health.toString().contains("<title id=\"title\">/inside</title>")) {
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

                        if (!(deployed1 && deployed2))
                            error("Failed to deploy.")


                    }
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
//        failure {
//            script {
//                if (env.Build == "true" && ISSUE_NUMBER) {
//                    prTools.comment(ISSUE_NUMBER,
//                            """{
//                                "body": "Jenkins failed during $currentBuild.displayName"
//                            }""",
//                            serviceName)
//                }
//                if(deploymentCheckpoint) { // don't restart instance on failure if no deployment occured
//                    commitHash = sh(script: "cat ~/userContent/$serviceName-last-success-hash.txt", returnStdout: true)
//                    commitHash = commitHash.substring(0, 7)
//                    echo "Rolling back to previous successful image. Hash: $commitHash"
//                    def cmd = """
//                            docker stop $serviceName;
//                            docker rm $serviceName;
//                            docker rmi -f \$(docker images -a -q);
//                            $startContainerCommand$commitHash
//                        """
//                    sh("ssh pi@carnivore.local '$cmd'")
//                    sh("ssh pi@herbivore.local '$cmd'")
//                }
//            }
//        }
        cleanup { // Cleanup post-flow always executes last
            deleteDir()
        }
    }
}