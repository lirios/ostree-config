pipeline {
  parameters {
    choice(name:'basearch', choices:['x86_64', 'aarch64'], description:'Architecture')
    choice(name:'channel', choices:['unstable', 'stable'], description:'Channel')
    choice(name:'variant', choices:['desktop', 'live', 'mobile', 'embedded'], description:'Variant')
  }
  agent {
    docker {
      image "liridev/ci-fedora-jenkins:31"
      args "--privileged -v ${JENKINS_HOME}:${JENKINS_HOME} --tmpfs /tmp -v /var/tmp:/var/tmp --device /dev/fuse --security-opt label:disable"
      alwaysPull true
    }
  }
  environment {
    GNUPGHOME = '/tmp/gnupg'
  }
  stages {
    stage('Prepare') {
      steps {
        sh label: 'Installation', script: 'sudo dnf install -y rpm-ostree gnupg2 pinentry'
        withCredentials([file(credentialsId: 'ci-pgp-key', variable: 'GPG_KEY'), file(credentialsId: 'ci-pgp-passphrase', variable: 'GPG_PASSPHRASE')]) {
          sh label: 'Configure GPG', script: """
mkdir -p ${GNUPGHOME}
gpg --import --no-tty --batch --yes ${GPG_KEY}
cat > ${GNUPGHOME}/gpg.conf <<EOF
pinentry-mode loopback
passphrase-file ${GPG_PASSPHRASE}
no-tty
batch
yes
EOF
echo test | gpg --clearsign
gpg --list-secret-keys --keyid-format SHORT
"""
        }
      }
    }
    stage('Build') {
      steps {
        script {
          repoPath = "${JENKINS_HOME}/workspace/ostree-artifacts/repo-dev"
          cacheDir = "${JENKINS_HOME}/workspace/ostree-artifacts/cache"
        }
        sh label: 'Build', script: """
          sudo --preserve-env=GNUPGHOME \
          ./build \
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
