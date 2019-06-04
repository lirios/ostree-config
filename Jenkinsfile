pipeline {
  parameters {
    string(name:'releasever', defaultValue:'30', description:'Fedora version')
    choice(name:'basearch', choices:['x86_64', 'aarch64'], description:'Architecture')
    choice(name:'channel', choices:['unstable', 'stable'], description:'Channel')
    choice(name:'variant', choices:['desktop', 'mobile', 'embedded'], description:'Variant')
  }
  agent {
    docker {
      image "fedora:${params.releasever}"
      args "--privileged --user root -v ${JENKINS_HOME}:${JENKINS_HOME}"
    }
  }
  stages {
    stage('Build') {
      steps {
        sh label: 'Installation', script: 'dnf install -y rpm-ostree rsync openssh-clients'
        script {
          repoPath = "${JENKINS_HOME}/workspace/ostree-artifacts/repo-dev"
          repoProdPath = "${JENKINS_HOME}/workspace/ostree-artifacts/repo-prod"
        }
        withCredentials([sshUserPrivateKey(credentialsId: 'ostree-repo-ssh', keyFileVariable: 'KEY_FILE')]) {
          sh label: 'Build', script: """
            export RSYNC_SSH_COMMAND='ssh -i ${KEY_FILE} -o StrictHostKeyChecking=no'
            ./make-tree --channel=${params.channel} \
                        --basearch=${params.basearch} \
                        --variant=${params.variant} \
                        --prod-url=${env.OSTREE_REPO_URL} \
                        --dev-repo=${repoPath} \
                        --prod-repo=${repoProdPath}
"""
        }
      }
    }
  }
  post {
    always {
      sh label: 'Remove local repositories', script: "rm -rf ${repoProdPath}"
    }
  }
}
