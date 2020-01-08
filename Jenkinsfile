pipeline {
  parameters {
    string(name:'releasever', defaultValue:'31', description:'Fedora version')
    choice(name:'basearch', choices:['x86_64', 'aarch64'], description:'Architecture')
    choice(name:'channel', choices:['unstable', 'stable'], description:'Channel')
    choice(name:'variant', choices:['desktop', 'live', 'mobile', 'embedded'], description:'Variant')
  }
  agent {
    docker {
      image "liridev/ci-fedora-jenkins:${params.releasever}"
      args "--privileged -v ${JENKINS_HOME}:${JENKINS_HOME} --tmpfs /tmp -v /var/tmp:/var/tmp --device /dev/fuse --security-opt label:disable"
    }
  }
  stages {
    stage('Build') {
      steps {
        sh label: 'Installation', script: 'sudo dnf install -y rpm-ostree rsync openssh-clients selinux-policy selinux-policy-targeted policycoreutils'
        script {
          repoPath = "${JENKINS_HOME}/workspace/ostree-artifacts/repo-dev"
          cacheDir = "${JENKINS_HOME}/workspace/ostree-artifacts/cache"
        }
        withCredentials([sshUserPrivateKey(credentialsId: 'ostree-repo-ssh', keyFileVariable: 'KEY_FILE')]) {
          sh label: 'Build', script: """
            sudo ./build \
                --remote-url https://repo.liri.io/ostree/repo \
                --mirror-ref lirios/${params.channel}/${params.basearch}/${params.variant} \
                --treefile lirios-${params.channel}-${params.variant}.yaml \
                --repodir ${repoPath}
            sudo ostree --repo=${repoPath} prune --keep-younger-than=1s
"""
        }
      }
    }
  }
  post {
    always {
      sh label: 'Remove local repositories', script: "sudo rm -rf ${repoProdPath}"
    }
  }
}
