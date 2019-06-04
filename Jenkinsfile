pipeline {
  triggers {
    cron '''TZ=Europe/Rome
H H * * *'''
  }
  parameters {
    string(name:'releasever', defaultValue:'30', description:'Fedora version')
    choice(name:'channel', choices:['unstable', 'stable'], description:'Channel')
    choice(name:'variant', choices:['desktop', 'mobile', 'embedded'], description:'Variant')
  }
  agent {
    docker {
      image "fedora:${params.releasever}"
      args '--privileged --user root'
    }
  }
  stages {
    stage('Install tools') {
      steps {
        sh 'dnf install -y git rpm-ostree'
      }
    }
    stage('Create') {
      steps {
        sh 'ostree init --repo=repo --mode=bare-user'
        sh "mkdir -p cache && rpm-ostree compose tree --force-nocache --repo=repo --cachedir=cache lirios-${params.channel}-${params.variant}.yaml"
      }
    }
  }
}
