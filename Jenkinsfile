pipeline {
  parameters {
    string(name:'releasever', defaultValue:'31', description:'Fedora version')
    choice(name:'basearch', choices:['x86_64', 'aarch64'], description:'Architecture')
    choice(name:'channel', choices:['unstable', 'stable'], description:'Channel')
    choice(name:'variant', choices:['desktop', 'live', 'mobile', 'embedded'], description:'Variant')
  }
  agent {
    docker {
      image "fedora:${params.releasever}"
      args "--privileged --user root -v ${JENKINS_HOME}:${JENKINS_HOME} --tmpfs /tmp -v /var/tmp:/var/tmp --device /dev/fuse --security-opt label:disable"
    }
  }
  stages {
    stage('Build') {
      steps {
        sh label: 'Installation', script: 'dnf install -y rpm-ostree rsync openssh-clients selinux-policy selinux-policy-targeted policycoreutils'
        script {
          repoPath = "${JENKINS_HOME}/workspace/ostree-artifacts/repo-dev"
          repoProdPath = "${JENKINS_HOME}/workspace/ostree-artifacts/repo-prod"
          cacheDir = "${JENKINS_HOME}/workspace/ostree-artifacts/cache"
        }
        withCredentials([sshUserPrivateKey(credentialsId: 'ostree-repo-ssh', keyFileVariable: 'KEY_FILE')]) {
          sh label: 'Build', script: """
            ./build \
                --remote-url https://repo.liri.io/ostree/repo \
                --mirror-ref lirios/${params.channel}/${params.basearch}/${params.variant} \
                --treefile lirios-${params.channel}-${params.variant}.yaml \
                --repodir ${repoPath} --cachedir ${cacheDir}
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
